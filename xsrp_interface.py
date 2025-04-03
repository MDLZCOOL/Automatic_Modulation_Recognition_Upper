from __future__ import division
import numpy as np
import socket


class XSRPDeviceInterface:
    """
    Interface for communicating with XSRP device
    """

    def __init__(self, pc_ip='192.168.1.180', xsrp_ip='192.168.1.166', timeout=5):
        """
        Initialize the XSRP device interface
        
        Args:
            pc_ip (str): IP address of the PC
            xsrp_ip (str): IP address of the XSRP device
            timeout (int): Socket timeout in seconds
        """
        self.pc_ip = pc_ip
        self.xsrp_ip = xsrp_ip
        self.timeout = timeout
        self.max_len = 192
        self.sample_length = self.max_len * 160

        # Setup UDP socket
        self.udp_addr = (self.pc_ip, 12345)
        self.dest_addr = (self.xsrp_ip, 13345)
        self.udp_socket = None

    def _setup_socket(self):
        """Set up the UDP socket for communication"""
        if self.udp_socket:
            self.udp_socket.close()

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(self.udp_addr)
        self.udp_socket.settimeout(self.timeout)

    def _send_command(self, hex_command="000099bb66010001008000F00000000000000000"):
        """
        Send a command to the device
        
        Args:
            hex_command (str): Hexadecimal command string
            
        Returns:
            bool: True if command was sent successfully
        """
        if not self.udp_socket:
            self._setup_socket()

        try:
            send_data = bytes.fromhex(hex_command)
            self.udp_socket.sendto(send_data, self.dest_addr)
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False

    def _receive_data(self, expected_size=None):
        """
        Receive data from the device
        
        Args:
            expected_size (int): Expected size of data in bytes
            
        Returns:
            bytes: Received data
        """
        if not self.udp_socket:
            self._setup_socket()

        recv_data_all = None

        try:
            for package_id in range(128):
                try:
                    recv_data, source = self.udp_socket.recvfrom(960)  # 960 bytes max per packet
                    if recv_data_all:
                        recv_data_all = recv_data_all + recv_data
                    else:
                        recv_data_all = recv_data

                    # If we have received the expected amount of data, stop
                    if expected_size and len(recv_data_all) >= expected_size:
                        break

                except socket.timeout:
                    print("Timeout occurred, no data received.")
                    break
        except Exception as e:
            print(f"Error receiving data: {e}")

        return recv_data_all

    def _process_raw_data(self, raw_data):
        """
        Process raw data received from the device
        
        Args:
            raw_data (bytes): Raw data from device
            
        Returns:
            tuple: Processed I and Q data arrays
        """
        if not raw_data:
            return None, None

        # Convert bytes to uint8
        recv_data_all_uint8 = np.frombuffer(raw_data, dtype=np.uint8)

        # Convert to double
        recv_data_all_double = np.array(recv_data_all_uint8, dtype=np.double)

        # Process I and Q components
        data_length = len(recv_data_all_double) // 4
        udp_data_ri = np.zeros(data_length)
        udp_data_rq = np.zeros(data_length)

        for m in range(data_length):
            udp_data_ri[m] = recv_data_all_double[m * 4] * 256 + recv_data_all_double[m * 4 + 1]
            udp_data_rq[m] = recv_data_all_double[m * 4 + 2] * 256 + recv_data_all_double[m * 4 + 3]

            # Handle negative numbers
            if udp_data_ri[m] >= 2049:
                udp_data_ri[m] = udp_data_ri[m] - 4096
            if udp_data_rq[m] >= 2049:
                udp_data_rq[m] = udp_data_rq[m] - 4096

        # Normalize
        udp_data_ri = udp_data_ri / 2047
        udp_data_rq = udp_data_rq / 2047

        # Reshape
        udp_data_ri = np.reshape(udp_data_ri, (self.max_len, 160))
        udp_data_ri = udp_data_ri[:, 32:160]
        udp_data_rq = np.reshape(udp_data_rq, (self.max_len, 160))
        udp_data_rq = udp_data_rq[:, 32:160]

        return udp_data_ri, udp_data_rq

    def get_data(self, command_hex=None, window_length=192):
        """
        Get data from the device
        
        Args:
            command_hex (str): Optional hex command to send before receiving data
            window_length (int): Optional window length of received data
            
        Returns:
            dict: Dictionary containing the received data
                - 'i_data': I component data
                - 'q_data': Q component data
                - 'combined': Combined I and Q data
                - 'normalized': Normalized data array
        """
        self._setup_socket()

        # Send command if provided, otherwise use default
        if command_hex:
            self._send_command(command_hex)
        else:
            self._send_command()

        # Receive data
        raw_data = self._receive_data(expected_size=self.sample_length * 4)

        if not raw_data or len(raw_data) != self.sample_length * 4:
            print(f"Error: Received {len(raw_data) if raw_data else 0} bytes, expected {self.sample_length * 4}")
            return None

        # Process data
        udp_data_ri, udp_data_rq = self._process_raw_data(raw_data)

        # Flatten I and Q data
        result_i = udp_data_ri[0]
        result_q = udp_data_rq[0]

        for n in range(1, window_length):
            result_i = np.hstack((result_i, udp_data_ri[n]))
            result_q = np.hstack((result_q, udp_data_rq[n]))

        # Combined data
        result = np.hstack((result_q, result_i))

        # Create normalized 2D array
        data = np.zeros((self.max_len, 256))
        for i in range(self.max_len):
            for j in range(128):
                data[i][j] = udp_data_ri[i][j]
                data[i][j + 128] = udp_data_rq[i][j]

        # Normalize each row
        for i in range(data.shape[0]):
            max_val = np.max(np.abs(data[i]))
            if max_val > 0:
                data[i] = data[i] / max_val

        return {
            'i_data': result_i,
            'q_data': result_q,
            'combined': result,
            'normalized': data.astype(np.float32)
        }

    def close(self):
        """Close the UDP socket"""
        if self.udp_socket:
            self.udp_socket.close()
            self.udp_socket = None


# Example usage
if __name__ == '__main__':
    # Create device interface
    device = XSRPDeviceInterface()

    # Get data from device (please note window_length)
    data = device.get_data(window_length=2)

    if data:
        print(f"I data shape: {data['i_data'].shape}")
        print(f"Q data shape: {data['q_data'].shape}")
        print(f"Combined data shape: {data['combined'].shape}")
        print(f"Normalized data shape: {data['normalized'].shape}")

    # Close the connection
    device.close()
