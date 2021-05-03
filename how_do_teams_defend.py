import streamlit as stimport pandas as pdimport numpy as npimport mathimport matplotlib.pyplot as pltcombined_df = pd.read_csv('https://raw.githubusercontent.com/rolekanma/HowDoTeamsDefend/master/data/All17WeeksFinal.csv')#combined_df = pd.read_csv('/Users/richardolekanma/Downloads/nfl-big-data-bowl-2021/All17WeeksFinal.csv')def dist(pos1, pos2):    val = math.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)    return valdef new_targets(s):    if s.targeted == "Not Targeted":        return 1 - s.Percent    else:        return s.Percent    @st.cachedef Defender_dist(Team, Pos):    #offense = ['RB', 'FB', 'WR', 'TE', 'HB']    defense = ['SS','FS', 'MLB', 'CB', 'LB', 'OLB', 'ILB','DB', 'S']    data = []    for game in combined_df.query('event == "pass_forward" and offense == @Team').gameId.unique():        #print(game)        for play in combined_df.query('event == "pass_forward" and offense == @Team and gameId == @game').playId.unique():            def_dict = {}            off_dict = {}            small_d = {}            #print(play)            for x in defense:                defense_data = combined_df.query('position == @x and event == "pass_forward" and offense == @Team and gameId == @game and playId == @play')[['x', 'y', 'position', 'displayName', 'o']].values                if defense_data.shape[0] == 1:                    d_pos = defense_data[0][2]                    def_xy = defense_data[0][0:2]                    def_name = defense_data[0][3]                    def_o = defense_data[0][4]                    def_dict[def_name] = [play, def_xy, d_pos, def_o]                elif defense_data.shape[0] == 0:                    pass                else:                    for x in range(defense_data.shape[0]):                        d_pos = defense_data[x][2]                        def_xy = defense_data[x][0:2]                        def_name = defense_data[x][3]                        def_o = defense_data[x][4]                        def_dict[def_name] = [play,def_xy, d_pos,def_o]            offense_data = combined_df.query('position == @Pos and event == "pass_forward" and offense == @Team and gameId == @game and playId == @play')[['x', 'y', 'position', 'displayName', 'o','route','passResult','target']].values            if offense_data.shape[0] == 1:                o_pos = offense_data[0][2]                off_xy = offense_data[0][0:2]                off_name = offense_data[0][3]                off_o = offense_data[0][4]                off_route = offense_data[0][5]                off_passresult = offense_data[0][6]                off_target = offense_data[0][7]                off_dict[off_name] = [play,off_xy, o_pos, off_o,off_route, off_passresult, off_target]            elif offense_data.shape[0] == 0:                pass            else:                for x in range(offense_data.shape[0]):                    o_pos = offense_data[x][2]                    off_xy = offense_data[x][0:2]                    off_name = offense_data[x][3]                    off_o = offense_data[x][4]                    off_route = offense_data[x][5]                    off_passresult = offense_data[x][6]                    off_target = offense_data[x][7]                    off_dict[off_name] = [play,off_xy, o_pos, off_o,off_route, off_passresult,  off_target]            for o_name, o_xy in off_dict.items() :                                if len(def_dict) == 0:                    pass                else:                    for d_name, d_xy in def_dict.items():                        d_dist = dist(o_xy[1],d_xy[1])                        small_d[d_name,d_xy[0], d_xy[2],] = [d_dist]                    total_player = min(small_d.items(), key=lambda x: x[1])                    closest_name = total_player[0]                    closest_xy = total_player[1]                    #print(o_xy[6])                    data.append([game, play, o_name, o_pos, o_xy[4], closest_name[0],closest_name[2],closest_xy[0],  o_xy[6],o_xy[5]])    output = pd.DataFrame(data, columns = ['gameId', 'playId', 'offensePlayerName', 'position', 'route',  'defenderName', 'defenderPosition','defenderDistance','targeted','passResult'])        #Nans for route are when defender is blocking can be dropped    output = output[output['route'].notna()]    df1 = output.groupby('route').defenderPosition.value_counts(normalize = True ).to_frame()        df3 = output.groupby(['route','defenderPosition']).targeted.value_counts(normalize = True ).to_frame()        df4 = df1.join(df3, how='inner')    #df4 = df6.join(df5, how='inner')        df4 = df4.rename(columns = {"defenderPosition":"DefenderCoveragePercent", 'targeted':'Percent'})    #df4['DefenderCoveragePercent'] = df4['DefenderCoveragePercent']    #df4['Percent'] = df4['Percent']  #  df4['DefenderCoveragePercent'] = df4['DefenderCoveragePercent'].round(decimals=2)  #  df4['Percent'] = df4['Percent'].round(decimals=2)    df4.reset_index(inplace = True)            df4['TargetPercent'] = df4.apply(new_targets, axis=1)    #df4['CompletionPercentage'] = df4.apply(compPercent, axis=1).round(decimals = 2)    df4.drop(['targeted','Percent'], axis = 1, inplace = True)    df4.drop_duplicates(keep = "first", inplace = True)    df4.sort_values(by =['TargetPercent'], ascending = False, inplace = True)    return df4def addbackgroundcolor(df):    return df.style.background_gradient(cmap='Blues').format({'TargetPercent':"{:.2%}", 'DefenderCoveragePercent':"{:.2%}"})                 nfl_teams = ['ATL', 'PHI', 'NO', 'TB', 'JAX', 'NYG', 'TEN', 'MIA', 'PIT', 'CLE','CIN', 'IND', 'BAL', 'BUF', 'NE', 'HOU', 'WAS', 'ARI', 'CAR',       'DAL', 'GB', 'CHI', 'NYJ', 'DET', 'OAK', 'LA']st.title('Looking At How Route Were Defended And Target Rates in 2018')st.text("")team = st.selectbox('Offensive Team', nfl_teams)pos = st.radio('Offensive Position', ['RB', 'FB', 'WR', 'TE'])# Create a text element and let the reader know the data is loading.data_load_state = st.text('Loading NFL data...')data = Defender_dist(team, pos)# Notify the reader that the data was successfully loaded.data_load_state.text("Done!")st.subheader('References')st.text('RouteRan: The Route the offensive player ran on the play')st.text('DefenderPosition: The most frequent nearest defender to that route when the ball is caught')st.text('DefenderCoveragePercent: Percentage the defender guarded that route')st.text('TargetPercent: The percent the offensive player was targeted while being guarded by the defender for that route')#Shows data in DF or whatever formst.subheader('How Teams Defended data')st.dataframe(addbackgroundcolor(data), width=1024, height=768)#st.dataframe(data, width=1024, height=768)