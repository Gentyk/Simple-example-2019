import pandas as pd
from pandas import DataFrame

def main(filename, big_sheet, company_sheet, result_filename):
    xl = pd.ExcelFile(filename)
    sheet_names = xl.sheet_names  # see all sheet names
    print(sheet_names)

    # КИМПАНИИ
    companies_df = xl.parse(company_sheet)#,  # лист с наименованием фирм
                            #skiprows=1)
    print(companies_df)
    companies = [i.strip() for i in list(companies_df['Примечание'])]
    print(companies)

    # файл
    big_df = xl.parse(big_sheet,
                      skiprows=2)
    # 1. получим конечные даты для команий из списка
    big_df['Примечание'] = big_df['Примечание'].apply(lambda x: x.strip())
    #big_df= big_df[big_df["Остаток"] != 0]
    orig = big_df.loc[big_df['Примечание'].isin(companies)]
    date = list(pd.unique(orig['Дата кон.']))
    date = [pd.to_datetime(x) for x in date]
    date.sort()
    print(date)


    # формирование выходного файла
    columns = {"id": None, "name": None}
    Global_GF = DataFrame()
    for d in date:
        columns[d] = 0
    columns['итог'] = 0
    columns['план'] = 0
    for company in companies:
        new_table_data = []
        data_df = big_df.loc[big_df['Примечание'].isin([company])]
        print(company, data_df['План'].sum())
        ids = list(pd.unique(data_df['Id_125']))

        # далее формируем строки
        for id in ids:
            new_row = columns.copy()
            data_df_by_id = data_df[data_df['Id_125'] == id]
            summ = 0
            summ_plan = 0
            for ind in range(len(data_df_by_id)):
                x = data_df_by_id.iloc[ind]
                #print("!!!", x['Дата кон.'], type(x['Дата кон.']))
                new_row[x['Дата кон.']] += int(x['Остаток'])
                summ += int(x['Остаток'])
                summ_plan += int(x['План'])
                if not new_row['name']:
                    new_row['name'] = x['Наименование']
            new_row['id'] = id
            new_row['итог'] = summ
            new_row['план'] = summ_plan
            new_table_data.append(new_row.copy())
        local_DF = DataFrame(new_table_data.copy())

        # итоговые результаты на компанию
        new_row = columns.copy()
        #new_row['id'] = company
        summ = 0

        for d in date:
            new_row[d] = local_DF[d].sum()
            summ += local_DF[d].sum()
        new_row['план'] = local_DF['план'].sum()
        new_row['id'] = company + ' План ' + str(local_DF['план'].sum()) + "              Итог осталось"
        new_row['итог'] = summ
        local_DF = local_DF.append(new_row.copy(), ignore_index=True)
        #print(local_DF)
        Global_GF = Global_GF.append(local_DF.copy())

    new_column_names = []
    for i in columns:
        if i in date:
            day = str(i.day)
            month = str(i.month)
            if  len(day) == 1:
                day = "0"+day
            if  len(month) == 1:
                month = "0"+month                
            new_column_names.append(f'{day}.{month}.{i.year}')
        else:
            new_column_names.append(i)
    Global_GF.columns = new_column_names
    print(Global_GF.columns)
    with pd.ExcelWriter(result_filename) as writer:
        Global_GF.to_excel(writer, index=False)

if __name__ == '__main__':
    filename = "6vip.xls"   # имя входного файла или путь
    big_sheet_name = "13 09"    # имя листа с большой таблицей
    company_sheet_name = "Sheet2"   # имя , где лежат имена фирм
    result_filename = "output.xls"
    main(filename, big_sheet_name, company_sheet_name, result_filename)

