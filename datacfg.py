import csv


class DataCfg:
    ind_num_tel = 0           # номер телефона
    ind_fio_manager = 1       # ФИО МПП
    ind_fio_rg = 2            # ФИО РГ
    ind_plan_result_call = 3  # плановое кол-во результативных звонков в получасе

    def __init__(self, fio_manager, fio_rg, num_tel, plan_result_call):
        self.fio_manager = fio_manager
        self.fio_rg = fio_rg
        self.num_tel = num_tel
        self.plan_result_call = plan_result_call

    @classmethod
    def from_tuple(cls, row):
        """ Метод для создания экземпляра DataCfg
            из строки csv-файла"""
        return cls(
            row[cls.ind_fio_manager],
            row[cls.ind_fio_rg],
            row[cls.ind_num_tel],
            row[cls.ind_plan_result_call]
        )


def get_cfg_list(csv_filename):
    """ чтение конфиг файла - возвращает словарь , ключом которого является номер телефона"""
    with open(csv_filename) as csv_fd:
        # создаем объект csv.reader для чтения csv-файла
        reader = csv.reader(csv_fd, delimiter=';')
        # это наш список, который будем возвращать
        cfg_list = {}
        # обрабатываем csv-файл построчно
        for row in reader:
            try:
                # создаем и добавляем объект в inputdata_list
                cfg_list[row[DataCfg.ind_num_tel]] = DataCfg.from_tuple(row)
            except (ValueError, IndexError):
                # если данные некорректны, то игнорируем их
                pass
    return cfg_list


if __name__ == "__main__":
    datacfg = get_cfg_list("cfg/list-num-tel.cfg")
    print(datacfg)
