from data.info import Infos

if __name__ == '__main__':
    infos = Infos()
    infos.resolve_date_stock_dict()
    for date_key in infos.date_stock_dict.keys():
        for stock_name in infos.stock_names:
            if stock_name in infos.date_stock_dict[date_key]:
                print infos.date_stock_dict[date_key][stock_name]