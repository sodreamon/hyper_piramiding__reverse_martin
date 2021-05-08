'''
진입이후 2틱 손실 마다 첫 진입 포지션의 1/5 만큼 청산(결국 10틱 손실시 전량 청산)
2틱 이득시 직전 포지션과 동일한 양 만큼 추가 진입 이후 2틱 이득시 마다 동일하게 직전 포지션과 동일한 양만큼 추가 진입
2틱 이상 이득이후 1틱 손실시 청산
'''
for _importing in [0]:

    import random
    import pandas as pd
    import numpy as np
    import os
    # db
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    # 차트
    import chart_studio.plotly as py
    import plotly.graph_objs as go
    import cufflinks as cf
    cf.go_offline(connected=True)

for _base in [0] :
    # 차트생성시 틱 수
    chart_data_len = 100000
    # 자본금
    bal = 10000000000
    # 회당 손절 사이즈
    sl_size = 1/5

for _db in [0]:

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///result.db'
    db = SQLAlchemy(app)


    class ResultData(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        data = db.Column(db.PickleType, nullable=False)

    if os.path.isfile("result.db"):
        os.remove("result.db")
    db.create_all()

for _def_box in [0]:

    #차트데이터 생성
    def making_new_chart_data(chart_data_len):

        data_sr = pd.Series({0:0})
        first_data_price = 0

        for r1 in range(0,chart_data_len) :
        
            _1_or_2 = random.randint(1,2)

            if _1_or_2 == 1 :
                
                first_data_price += 1
                data_sr = data_sr.append(pd.Series({0:first_data_price}), ignore_index=True)

            else :

                first_data_price -= 1
                data_sr = data_sr.append(pd.Series({0:first_data_price}), ignore_index=True)

            print("\r",r1,end="")
        print()

        return data_sr

    # 트레이딩
    def trading(chart_data_sr, bal, sl_size) :
        
        trading_df = pd.DataFrame(columns=["PiramidingCount", "Profit", "Balance"])
        trading_bal = bal * 1
        position_list = []
        position_close_list = []
        lowest_price = float("inf")

        monitoring_df = pd.DataFrame() # 해당 전략이 정상적으로 작동하는지 확인하는 데이터프레임

        for _index_num in range(1,len(chart_data_sr)) :

            pre_price = chart_data_sr.iloc[_index_num-1]
            _price = chart_data_sr.iloc[_index_num]

            if len(position_list) < 1 :
                position_list.append([10, pre_price]) # [포지션사이즈, 진입가격]

            if pre_price < lowest_price :
                lowest_price = pre_price # 포지션 진입 중 최저가격 찾기

            if _price < pre_price :
                
                if len(position_list) == 1 : # 진입이후 피라미딩 횟수 0

                    if len(position_close_list) < 1 : # 아직 한번도 청산한 적이 없음

                        if position_list[0][1] - _price == 2 :  # 첫 진입 가격으로부터 -2틱

                            close_size = position_list[0][0] * sl_size # 첫 포지션의 sl_size 만큼 손절
                            closed_price = _price
                            loss_tick = _price - position_list[0][1]
                            profit = loss_tick * close_size

                            trading_bal += profit
                            trading_df = trading_df.append({"PiramidingCount":len(position_list)-1, "Profit":profit, "Balance":trading_bal},ignore_index=True)

                            position_close_list.append([close_size, _price]) # [청산 사이즈, 청산 가격]
                            position_list[0][0] = position_list[0][0] - close_size # 첫 포지션 사이즈 수정(원래사이즈 - 청산된사이즈)

                    elif len(position_close_list) >= 1 :

                        if position_close_list[-1][1] - _price == 2 : # 직전 손절 가격에서 -2틱

                            close_size = position_close_list[-1][0] # 직전 청산 사이즈와 동일
                            closed_price = _price
                            loss_tick = _price - position_list[0][1]
                            profit = loss_tick * close_size

                            trading_bal += profit
                            trading_df = trading_df.append({"PiramidingCount":len(position_list)-1, "Profit":profit, "Balance":trading_bal},ignore_index=True)

                            position_close_list.append([close_size, _price]) # [청산 사이즈, 청산 가격]
                            position_list[0][0] = position_list[0][0] - close_size # 첫 포지션 사이즈 수정(이전에 청산된 사이즈 - 이번에 청산된사이즈)

                        if position_list[0][0] <= 0 : # 포지션이 모두 청산 됬을 때

                            # profit = 0 # 손실 구하기
                            # for closed_position in position_close_list :
                            #     closed_size = closed_position[0][0]
                            #     closed_price = closed_position[0][1]
                            #     first_position_price = position_list[0][1]
                            #     loss_tick = closed_price - first_position_price
                            #     loss = loss_tick * closed_size
                            #     profit += loss

                            # trading_bal += profit

                            # trading_df = trading_df.append({"PiramidingCount":len(position_list)-1, "Profit":profit, "Balance":trading_bal},ignore_index=True)

                            position_list = []
                            position_close_list = []
                            lowest_price = float("inf")



                elif len(position_list) > 1 : # 피라미딩이 1번 이상 진행된 이후 첫 하락

                    profit = 0 # 최종 수익률

                    for _position in position_list : # 이득 포지션 먼저

                        position_size = _position[0] # 개별 포지션 사이즈
                        position_price = _position[1] # 개별 포지션 진입 가격

                        _position_profit = (_price - position_price) * position_size # 개별 포지션 손익

                        profit += _position_profit

                    # for closed_position in position_close_list : # 손실 구하기
                    #     closed_size = closed_position[0][0]
                    #     closed_price = closed_position[0][1]
                    #     first_position_price = position_list[0][1]
                    #     loss_tick = closed_price - first_position_price
                    #     loss = loss_tick * closed_size
                    #     profit += loss

                    trading_bal += profit

                    trading_df = trading_df.append({"PiramidingCount":len(position_list)-1, "Profit":profit, "Balance":trading_bal},ignore_index=True)

                    position_list = []
                    position_close_list = []
                    lowest_price = float("inf")

            if _price > pre_price : 
                
                if len(position_list) == 1 : # 현재 진입된 포지션이 처음 하나이고
                    if lowest_price + 2 == _price : # 포지션 진입 이후 최저가에서 2틱 이득 본 경우

                        position_size = position_list[0][0]

                        position_list.append([position_size,_price])

                elif len(position_list) > 1 : # 현재 진입된 포지션이 1번이상 피라미딩이 되었을 경우
                    
                    last_position_price = position_list[-1][1] # 마지막으로 오픈된 포지션 가격

                    if _price == last_position_price+2 : # 마지막으로 오픈된 포지션 가격에서 2틱 이득 본 경우

                        position_size = 0 # 기존 모든 포지션의 포지션 사이즈 합 만큼 포지션을 정함
                        for _position in position_list :
                            position_size_1 = _position[0]
                            position_size += position_size_1

                        position_list.append([position_size,_price])
            
            # 모니터링
            # monitoring_df = monitoring_df.append({
            #     "Price":_price,
            #     # "PiramidingCount":len(position_list)-1,
            #     "Balance":format(trading_bal,","),
            #     "FirstPositonPrice": (lambda x: x[0][1] if len(x)>0 else np.nan)(position_list),
            #     "Position_size":(lambda x: sum([i[0] for i in x]) if len(x)>0 else np.nan)(position_list),
            #     "Equity": (lambda x: format(sum([i[0]*(_price-i[1]) for i in x])+trading_bal,",") if len(x)>0 else np.nan)(position_list),
            #     # "PositionList":position_list
            #     },ignore_index=True)
            print("\r",_index_num,end="")
            # print({
            #     "Price":_price,
            #     # "PiramidingCount":len(position_list)-1,
            #     "Balance":format(trading_bal,","),
            #     "FirstPositonPrice": (lambda x: x[0][1] if len(x)>0 else np.nan)(position_list),
            #     "Position_size":(lambda x: sum([i[0] for i in x]) if len(x)>0 else np.nan)(position_list),
            #     "Equity": (lambda x: format(sum([i[0]*(_price-i[1]) for i in x])+trading_bal,",") if len(x)>0 else np.nan)(position_list),
            #     "position_close_list":position_close_list,
            #     "position_list":position_list
            #     # "PositionList":position_list
            #     })

        print()

        # pd.set_option("display.max_rows",100000000000)
        # # pd.set_option("display.max_columns",6)
        # print(monitoring_df)

        return trading_df
                



for _main_process in [0] :

    chart_data_sr = making_new_chart_data(chart_data_len)
    trading_df = trading(chart_data_sr, bal, sl_size)

    new_result = ResultData(data=trading_df)
    db.session.add(new_result)
    db.session.commit()

    print(trading_df)
    trading_df["Balance"].iplot(kind="line")