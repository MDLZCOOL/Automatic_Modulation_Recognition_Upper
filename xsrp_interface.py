import numpy as np
import socket


class XSRPDeviceGetData:
    def __init__(self, window_length: int):
        self.pc_ip = '192.168.1.180'
        self.xsrp_ip = '192.168.1.166'
        self.window_length = window_length
        self.max_len = 192
        self.result = None
        self.result_i = None
        self.result_q = None
        self.data_list = None
        self.label_list = []
        self.idx = 0

        udp_addr = (self.pc_ip, 12345)
        dest_addr = (self.xsrp_ip, 13345)
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(udp_addr)
        udp_socket.settimeout(5)
        while True:
            # sending commend begin
            hex_data = "000099bb66010001008000F00000000000000000"
            send_data = bytes.fromhex(hex_data)
            udp_socket.sendto(send_data, dest_addr)
            # sending end
            # receiving data begin
            recv_data_all = None
            for package_id in range(128):
                try:
                    recv_data, source = udp_socket.recvfrom(960)
                    if recv_data_all:
                        recv_data_all = recv_data_all + recv_data
                    else:
                        recv_data_all = recv_data
                except socket.timeout:
                    print("Timeout occurred, no data received.")
                    break
            if len(recv_data_all) == self.max_len * 160 * 4:
                break
        # receiving end
        recv_data_all_uint8 = np.zeros(len(recv_data_all))
        for i in range(len(recv_data_all)):
            recv_data_all_uint8[i] = np.uint8(recv_data_all[i])
        recv_data_all_double = np.array(recv_data_all_uint8, dtype=np.double)
        udp_data_ri = np.zeros(int(len(recv_data_all) / 4))
        udp_data_rq = np.zeros(int(len(recv_data_all) / 4))
        for m in range(int(len(recv_data_all) / 4)):
            udp_data_ri[m] = recv_data_all_double[m * 4] * 256 + recv_data_all_double[m * 4 + 1]
            udp_data_rq[m] = recv_data_all_double[m * 4 + 2] * 256 + recv_data_all_double[m * 4 + 3]
            if udp_data_ri[m] >= 2049:
                udp_data_ri[m] = udp_data_ri[m] - 4096
            if udp_data_rq[m] >= 2049:
                udp_data_rq[m] = udp_data_rq[m] - 4096
        udp_data_ri = udp_data_ri / 2047
        udp_data_rq = udp_data_rq / 2047
        udp_data_ri = np.reshape(udp_data_ri, (self.max_len, 160))
        udp_data_ri = udp_data_ri[:, 32:160]
        udp_data_rq = np.reshape(udp_data_rq, (self.max_len, 160))
        udp_data_rq = udp_data_rq[:, 32:160]

        # 使用window_length参数
        if self.window_length > self.max_len:
            self.window_length = self.max_len
            print(f"Warning: window_length exceeds max_len, setting to {self.max_len}")

        self.result_i = udp_data_ri[0]
        self.result_q = udp_data_rq[0]
        for n in range(1, self.window_length):
            self.result_i = np.hstack((self.result_i, udp_data_ri[n]))
            self.result_q = np.hstack((self.result_q, udp_data_rq[n]))
        self.result = np.hstack((self.result_i, self.result_q))

        data_ = np.zeros((self.max_len, 256))
        for i in range(self.max_len):
            for j in range(128):
                data_[i][j] = udp_data_ri[i][j]
                data_[i][j + 128] = udp_data_rq[i][j]
        for i in range(data_.shape[0]):
            data_[i] = data_[i] / np.max(data_[i])
        self.data_list = data_.astype(np.float32)

    def __next__(self):
        if self.idx >= len(self.data_list):
            raise StopIteration
        else:
            item = (self.data_list[self.idx], self.label_list[self.idx])
            self.idx = self.idx + 1
            return item

    def __iter__(self):
        self.idx = 0
        return self

    def __len__(self):
        return len(self.data_list)


# 示例调用
if __name__ == '__main__':
    data = XSRPDeviceGetData(window_length=8)
    print(f"result_i shape: {data.result_i.shape}")
    print(f"result_q shape: {data.result_q.shape}")
    print(f"result shape: {data.result.shape}")
