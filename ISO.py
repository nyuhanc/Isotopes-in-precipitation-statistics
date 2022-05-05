# Author Aljaž Pavšek, IJS (O2), 2019


print('ISOTOPES IN PRECIPITATION STATISTICS\n')

# Console input: filename and filename extension
fajlname = input('Name of Excel file (without the extension): ')
koncnica = '.xls'

# parameter: presence of all precipitation: False / True
if input('Is all precipitation present in the Excel file? (y/n) ') == 'y':
    all_perc = True
else:
    all_perc = False

# ----- IMPORTS -------------------------------------------------------------------------------------------------------
import numpy as np
import os.path
import matplotlib.pyplot as plt
import xlrd

# ----- DEFINITIONS OF STATISTICAL FUNCTIONS --------------------------------------------------------------------------

# Definitions of functions needed for reshaping and filtering the data

class Proc:

    def __init__(self,file_name):
        self.file_name = file_name
        wb = xlrd.open_workbook(file_name)
        sheet = wb.sheet_by_index(0)

        # unfiltered, raw data
        self.P = self.NA(sheet.col_values(5)[1:])
        self.T = self.NA(sheet.col_values(7)[1:])
        self.RH = self.NA(sheet.col_values(9)[1:])
        self.O_18 = self.NA(sheet.col_values(11)[1:])
        self.H_2 = self.NA(sheet.col_values(15)[1:])
        self.d = self.NA(sheet.col_values(19)[1:])
        self.H_3_TU = self.NA(sheet.col_values(26)[1:])


        self.Sample_ID = self.NA(sheet.col_values(0)[1:])
        self.Station_ID = self.NA(sheet.col_values(1)[1:])
        self.year = self.NA([int(i) for i in sheet.col_values(3)[1:]])
        self.month = self.NA([int(i) for i in sheet.col_values(4)[1:]])
        self.Date = self.reform_date()
        self.P_source_of_data = self.NA(sheet.col_values(6)[1:])
        self.T_source_of_data = self.NA(sheet.col_values(8)[1:])
        self.RH_source_of_data = self.NA(sheet.col_values(10)[1:])
        self.O_18_comment = self.NA(sheet.col_values(12)[1:])
        self.O_18_lab_name = self.NA(sheet.col_values(13)[1:])
        self.O_18_source_of_data = self.NA(sheet.col_values(14)[1:])
        self.H_2_comment = self.NA(sheet.col_values(16)[1:])
        self.H_2_lab_name = self.NA(sheet.col_values(17)[1:])
        self.H_2_source_of_data = self.NA(sheet.col_values(18)[1:])
        self.d_source_of_data = self.NA(sheet.col_values(20)[1:])
        self.H_3_TU_uncertainty = self.NA(sheet.col_values(27)[1:])
        self.H_3_TU_comment = self.NA(sheet.col_values(28)[1:])
        self.H_3_TU_lab_name = self.NA(sheet.col_values(29)[1:])
        self.H_3_TU_source_of_data = self.NA(sheet.col_values(30)[1:])
        self.Remarks = self.NA(sheet.col_values(31)[1:])


        # data reshaping and filtering - data preparation for further statistical anlysis

        self.P_proc = self.group_years(self.P)
        self.T_proc = self.group_years(self.T)

        # we apply this filter only if we have all precipitation amount info (for every moth)
        if all_perc:
            RH_proc = self.filter_8(self.filter_perc(self.group_years(self.RH)))
            O_18_proc = self.filter_8(
                self.filter_perc(self.group_years(self.O_18)))
            H_2_proc = self.filter_8(self.filter_perc(self.group_years(self.H_2)))
            d_proc = self.filter_8(self.filter_perc(self.group_years(self.d)))
            H_3_TU_proc = self.filter_8(
                self.filter_perc(self.group_years(self.H_3_TU)))
        else:
            RH_proc = self.filter_8(self.group_years(self.RH))
            O_18_proc = self.filter_8(self.group_years(self.O_18))
            H_2_proc = self.filter_8(self.group_years(self.H_2))
            d_proc = self.filter_8(self.group_years(self.d))
            H_3_TU_proc = self.filter_8(self.group_years(self.H_3_TU))

        self.RH_proc = RH_proc
        self.O_18_proc = O_18_proc
        self.H_2_proc = H_2_proc
        self.d_proc = d_proc
        self.H_3_TU_proc = H_3_TU_proc

        self.trio = self.filter_OandH()
        self.trio_by_y = self.filter_OandH_by_years()

        self.O_18_months = self.group_months(self.O_18_proc)
        self.H_2_months = self.group_months(self.H_2_proc)
        self.d_months = self.group_months(self.d_proc)
        self.H_3_months = self.group_months(self.H_3_TU_proc)


        # -----------------------------------------------------------------------------------------------------

    # if the value is missing, substitute '' for 'NA'
    def NA(self,list_in):
        list_out = []
        for j in list_in:
            if j == '': list_out.append('NA')
            else: list_out.append(j)

        return list_out

    def reform_date(self):
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']
        date = []
        for j in range(len(self.year)):
            date.append((months[int(self.month[j]) - 1] + ' ' + str(self.year[j])))

        return date

    # pack data in a dictionary of the form {'2000': {'1': 2.3, '2': 5.1, '3': 8.2,....}, '2001':{...}...}
    def group_years(self, a):  # a = array (of floats), y = array of years (of strings), m = array of years (of strings)
        y = self.year
        m = self.month
        if (len(a) == len(y)) and (len(y) == len(m)):
            grouped_dict = {}
            for i in y:
                grouped_dict[i] = {}
            for i in range(len(a)):
                grouped_dict[y[i]][m[i]] = a[i]
        else:
            print('--> error: length not same <--')
            return 0

        return grouped_dict

    def group_months(self,a):  # same shape as group_years
        out = [[] for i in range(13)]
        for i,j in a.items():
            out[0].append(i)
            for k,l in j.items():
                out[int(k)].append(l)
        return out

    # filter that filters out years for which there is less than 8 monthly data available
    def filter_8(self, d):  # d = dict, group_years
        filtered_8 = {}
        for i, j in d.items():
            num_NA = 0
            for k, l in j.items():
                if l == 'NA':
                    num_NA += 1

            if len(j) >= 8 and num_NA <= 4:
                filtered_8[i] = j

        return filtered_8

    # filter that filters out all years for which the total amount of precipitation corresponding
    # to each data value does not exceed 70% of total rainfall that year
    def filter_perc(self, d):  # d = dict, group_years_dict,
        filtered_perc = {}  # p_dict = dict, group_years_dict,
        for i, j in d.items():  # p_array = dict, group_years_array
            s1 = 0              # p must be precipitation data
            s2 = 0
            for k, l in j.items():
                s2 += self.P_proc[i][k]
                if l != 'NA':
                    s1 += self.P_proc[i][k]
            if s1 >= 0.7 * s2:
                filtered_perc[i] = j

        return filtered_perc

    # if, for a specific month, either H_2 ali O_18 is missing, we cannot take it into account when
    # calculating regression coefficients for LMWL (local meteoric water line)
    def filter_OandH(self):
        t = []
        for i,j in self.P_proc.items():
            if i in self.H_2_proc and i in self.O_18_proc:
                for m,n in j.items():
                    if m in self.H_2_proc[i] and m in self.O_18_proc[i]:
                        if not isinstance(self.O_18_proc[i][m], str) and not isinstance(self.H_2_proc[i][m], str):
                            t.append([n, self.O_18_proc[i][m], self.H_2_proc[i][m]])

        return t # returns result in form of 'trio' -> [ [perc, O, H], [perc ,O, H], [],....]

    # same as the function above + extra sorting by years
    def filter_OandH_by_years(self):
        t = {} #trio
        for i,j in self.P_proc.items():
            a = []
            if i in self.H_2_proc and i in self.O_18_proc:
                for m,n in j.items():
                    if m in self.H_2_proc[i] and m in self.O_18_proc[i]:
                        if not isinstance(self.O_18_proc[i][m], str) and not isinstance(self.H_2_proc[i][m], str):
                            a.append([n, self.O_18_proc[i][m], self.H_2_proc[i][m]])
            t[i] = a

        return t # returns result in form of 'trio by years'
                 # -> [ [[perc, O, H], [perc ,O, H], [],....], [[perc, O, H], [perc ,O, H], [],....],...]


# Definitions of statistical functions (different averages)
class Stat:
    def __init__(self, precipitation, data, rounded):
        try:
            if data != {}:
                self.w = precipitation  # of form 'group_years'
                self.d = data  # of form  'group_years'
                self.r = rounded  # numb. of decimals to round on
                self.ann_m = self.ANN_M()
                self.mon_m = self.MON_M()
                self.sea_m = self.SEA_M()
                self.m = self.M()
                if all_perc:
                    w_m = self.W_M()
                    w_ann_m = self.W_ANN_M()
                    w_mon_m = self.W_MON_M()
                    w_sea_m = self.W_SEA_M()
                else:
                    w_m = ('NA','NA')
                    w_ann_m = {}
                    w_mon_m = {}
                    w_sea_m = {}
                self.w_m = w_m
                self.w_ann_m = w_ann_m
                self.w_mon_m = w_mon_m
                self.w_sea_m = w_sea_m

            else:
                raise ValueError('--> Parameter "data" should not be empty! <--')
        except (ValueError, ZeroDivisionError):
            self.w = {}
            self.d = {}
            self.r = rounded
            self.ann_m = {}
            self.w_ann_m = {}
            self.mon_m = {}
            self.w_mon_m = {}
            self.sea_m = {}
            self.w_sea_m = {}
            self.m = ("/", 0)
            self.w_m = ("/", 0)
            self.years = []


    # Total mean
    # Return in form (value, numb. of samples)
    def M(self):
        s = 0
        c = 0
        for i,j in self.d.items():
            for m,n in j.items():
                if not isinstance(n, str):
                    s += n
                    c += 1

        return (round(s/c,self.r),c)

    # Total weighted mean
    # Return in form (value, numb. of samples)
    def W_M(self):
        s = 0
        W= 0
        c = 0
        for i, j in self.d.items():
            for m, n in j.items():
                if not isinstance(n, str):
                    s += n*self.w[i][m]
                    W += self.w[i][m]
                    c += 1

        return (round(s / W, self.r), c)

    # Annual mean
    # Return in form { '2000':[<avr. for year 2000>, n = numb. of samples], ....}
    def ANN_M(self):  # d je oblike 'group_year', r=mesto zaokroženih decimalk
        means = {}
        for i, j in self.d.items():
            s = 0
            c = 0
            for m, n in j.items():
                if not isinstance(n, str):
                    s += n
                    c += 1
            means[i] = [round(s / c, self.r), c]  # Note: round(2.675, 2) gives 2.67 instead of the expected 2.68

        return means

    # Weighted annual means
    # vReturn in form { '2000':[<avr. for year 2000>, n = numb. of samples], ....}
    def W_ANN_M(self):  # d, p of form 'group_year' (d=data, p = precipitation = weight), r = round on r decimals
        means = {}
        for i, j in self.d.items():
            s = 0
            c = 0
            W = 0
            for m, n in j.items():
                if not isinstance(n, str):
                    s += n * self.w[i][m]
                    W += self.w[i][m]
                    c += 1
            means[i] = [round(s / W, self.r), c]  # Note: round(2.675, 2) gives 2.67 instead of the expected 2.68

        return means

    # Monthly means
    # Return in form { 'Jan':[<avr. for January>, n = numb. of samples], ....}
    # Assumption: there is no month for which there is no data
    def MON_M(self):
        # group_months explicitly written down for the sake of clarity
        group_months = {1: [0, 0], 2: [0, 0], 3: [0, 0], 4: [0, 0], 5: [0, 0], 6: [0, 0], 7: [0, 0],
                        8: [0, 0], 9: [0, 0], 10: [0, 0], 11: [0, 0], 12: [0, 0]}
        for i, j in self.d.items():
            for m, n in j.items():
                if not isinstance(n, str):
                    group_months[m][0] += n
                    group_months[m][1] += 1

        means = {}
        for i, j in group_months.items():
            if j[1] > 0:
                means[i] = (round(j[0] / j[1], self.r), j[1])
            else:
                means[i] = ("NA", 0)

        return means  # dict of tuples

    # Weighted monthly means
    # Return in form { 'Jan':[<avr. for January>, n = numb. of samples], ....}
    # Assumption: there is no month for which there is no data
    def W_MON_M(self):
        group_months = {1: [0, 0, 0], 2: [0, 0, 0], 3: [0, 0, 0], 4: [0, 0, 0], 5: [0, 0, 0], 6: [0, 0, 0], 7: [0, 0, 0],
                        8: [0, 0, 0], 9: [0, 0, 0], 10: [0, 0, 0], 11: [0, 0, 0], 12: [0, 0, 0]}
        for i, j in self.d.items():
            for m, n in j.items():
                if not isinstance(n, str):
                    group_months[m][0] += n * self.w[i][m]
                    group_months[m][1] += 1
                    group_months[m][2] += self.w[i][m]

        means = {}
        for i, j in group_months.items():
            if j[1] > 0:
                means[i] = (round(j[0] / j[2], self.r), j[1])
            else:
                means[i] = ("NA", 0)

        return means  # dict of tuples

    # Seasonal means
    # Return in form { 'winter':[<avr. for winter>, n = numb. of samples], ....}
    # Assumption: there is no month for which there is no data
    def SEA_M(self):

        group_seasons = {'spring': [0, 0], 'summer': [0, 0], 'autumn': [0, 0], 'winter': [0, 0]}

        for i, j in self.d.items():
            for m, n in j.items():
                if not isinstance(n, str):
                    if m in (3,4,5):
                        group_seasons['spring'][0] += n
                        group_seasons['spring'][1] += 1
                    elif m in (6,7,8):
                        group_seasons['summer'][0] += n
                        group_seasons['summer'][1] += 1
                    elif m in (9,10,11):
                        group_seasons['autumn'][0] += n
                        group_seasons['autumn'][1] += 1
                    elif m in (12,1,2):
                        group_seasons['winter'][0] += n
                        group_seasons['winter'][1] += 1

        means = {}
        for i, j in group_seasons.items():
            if j[1] > 0:
                means[i] = (round(j[0] / j[1], self.r), j[1])
            else:
                means[i] = ("NA", 0)
        return means  # list of tuples

    # Weighted seasonal means
    # Return in form { 'winter':[<avr. for winter>, n = numb. of samples], ....}
    # Assumption: there is no month for which there is no data
    def W_SEA_M(self):

        group_seasons = {'spring': [0, 0, 0], 'summer': [0, 0, 0], 'autumn': [0, 0, 0], 'winter': [0, 0, 0]}

        for i, j in self.d.items():
            for m, n in j.items():
                if not isinstance(n, str):
                    if m in (3,4,5):
                        group_seasons['spring'][0] += n * self.w[i][m]
                        group_seasons['spring'][1] += 1
                        group_seasons['spring'][2] += self.w[i][m]
                    elif m in (6,7,8):
                        group_seasons['summer'][0] += n * self.w[i][m]
                        group_seasons['summer'][1] += 1
                        group_seasons['summer'][2] += self.w[i][m]
                    elif m in (9,10,11):
                        group_seasons['autumn'][0] += n * self.w[i][m]
                        group_seasons['autumn'][1] += 1
                        group_seasons['autumn'][2] += self.w[i][m]
                    elif m in (12,1,2):
                        group_seasons['winter'][0] += n * self.w[i][m]
                        group_seasons['winter'][1] += 1
                        group_seasons['winter'][2] += self.w[i][m]

        means = {}
        for i, j in group_seasons.items():
            if j[1] > 0:
                means[i] = (round(j[0] / j[2], self.r), j[1])
            else:
                means[i] = ("NA", 0)
        return means  # list of tuples

    def reform_annual_means(self):
        years = []
        values = []
        n = []
        for i, j in self.w.items():
            if i in self.ann_m:
                years.append(i)
                values.append(self.ann_m[i][0])
                n.append(self.ann_m[i][1])
            else:
                years.append(i)
                values.append("NA")
                n.append("NA")

        return [years, values, n]

    def reform_weighted_annual_means(self):
        values = []
        n = []
        for i, j in self.w.items():
            if i in self.w_ann_m:
                values.append(self.w_ann_m[i][0])
            else:
                values.append("NA")

        return values

# statistics for precipitation and temperature
class PandTStat:
    def __init__(self,precipitation,temperature,years):
        self.years = sorted(set(years))
        self.P = self.filter_8(precipitation)
        self.T = self.filter_8(temperature)
        try:
            if self.T != {}:
                self.T_m = self.M(self.T,2,True)
                self.T_ann_m = self.ANN_M(self.T,2,True)
                self.T_mon_m = self.MON_M(self.T,2,True)
                self.T_sea_m = self.SEA_M(self.T,2,True)
                reform_annual_means_T = self.reform_annual_means_T()
                self.T_years = reform_annual_means_T[0]
                self.T_ref_ann_m = reform_annual_means_T[1]
                self.T_ref_ann_m_n = reform_annual_means_T[2]
            else:
                raise ValueError('--> Parameter "data" should not be empty! <--')
        except ValueError:
            self.T_m = ("/",0)
            self.T_ann_m = {}
            self.T_mon_m = {}
            self.T_sea_m = {}
            self.T_years = []
            self.T_ref_ann_m = []
            self.T_ref_ann_m_n = []
        try:
            if self.P != {}:
                self.P_m = self.M(self.P,1,False)
                self.P_ann_m = self.ANN_M(self.P,1,False)
                self.P_mon_m = self.MON_M(self.P,1,False)
                self.P_sea_m = self.SEA_M(self.P,1,False)
                reform_annual_means_P = self.reform_annual_means_P()
                self.P_years = reform_annual_means_P[0]
                self.P_ref_ann_m = reform_annual_means_P[1]
                self.P_ref_ann_m_n = reform_annual_means_P[2]
            else:
                raise ValueError('--> Parameter "data" should not be empty! <--')
        except ValueError:
            self.P_m = ("/",0)
            self.P_ann_m = {}
            self.P_mon_m = {}
            self.P_sea_m = {}
            self.P_years = []
            self.P_ref_ann_m = []
            self.P_ref_ann_m_n = []



    # f# filter that filters out years for which there is less than 8 monthly data available
    # d = dict, group_years
    def filter_8(self, d):
        filtered_8 = {}
        for i, j in d.items():
            num_NA = 0
            for k, l in j.items():
                if l == 'NA':
                    num_NA += 1

            if len(j) >= 8 and num_NA <= 4:
                filtered_8[i] = j

        return filtered_8

    # Total mean
    # Return in form (value, numb. of samples)
    def M(self,d,r,norm):
        s = 0
        c = 0
        for i,j in d.items():
            for m,n in j.items():
                if not isinstance(n, str):
                    s += n
                    c += 1
        if norm: return (round(s/c,r),c)
        else: return (round(s/len(d),r),c)

    # Annual means
    # Return in form { '2000':[<avr. for year 2000>, n = numb. of samples], ....}
    # d of form 'group_year', r = round on r decimals
    def ANN_M(self,d,r,norm):
        means = {}
        for i, j in d.items():
            s = 0
            c = 0
            for m, n in j.items():
                if not isinstance(n, str):
                    s += n
                    c += 1
            if norm: means[i] = [round(s / c, r), c]
            else: means[i] = [round(s , r), c]

        return means

    # Monthly means
    # Return in form { 'Jan':[<avr. for January>, n = numb. of samples], ....}
    # Assumption: there is no month for which there is no data
    def MON_M(self,d,r,norm):
        # group_months explicitly writtenfor the sake of clarity
        group_months = {1: [0, 0], 2: [0, 0], 3: [0, 0], 4: [0, 0], 5: [0, 0], 6: [0, 0], 7: [0, 0],
                        8: [0, 0], 9: [0, 0], 10: [0, 0], 11: [0, 0], 12: [0, 0]}
        c1=0
        for i, j in d.items():
            for m, n in j.items():
                if not isinstance(n, str):
                    group_months[m][0] += n
                    group_months[m][1] += 1

        means = {}
        for i, j in group_months.items():
            if j[1] > 0:
                if norm: means[i] = (round(j[0] / j[1], r), j[1])
                else: means[i] = (round(j[0] / len(d), r), j[1])
            else:
                means[i] = ("NA", 0)

        return means  # dict of tuples

    # Seasonal means
    # Return in form { 'winter':[<avr. for winter>, n = numb. of samples], ....}
    # Assumption: there is no month for which there is no data
    def SEA_M(self,d,r,norm):
        group_seasons = {'spring': [0, 0], 'summer': [0, 0], 'autumn': [0, 0], 'winter': [0, 0]}
        for i, j in d.items():
            for m, n in j.items():
                if not isinstance(n, str):
                    if m in (3,4,5):
                        group_seasons['spring'][0] += n
                        group_seasons['spring'][1] += 1
                    elif m in (6,7,8):
                        group_seasons['summer'][0] += n
                        group_seasons['summer'][1] += 1
                    elif m in (9,10,11):
                        group_seasons['autumn'][0] += n
                        group_seasons['autumn'][1] += 1
                    elif m in (12,1,2):
                        group_seasons['winter'][0] += n
                        group_seasons['winter'][1] += 1
        means = {}
        for i, j in group_seasons.items():
            if j[1] > 0:
                if norm: means[i] = (round(j[0] / j[1], r), j[1])
                else: means[i] = (round(j[0] / len(d), r), j[1])
            else:
                means[i] = ("NA", 0)

        return means  # dict of tuples

    def reform_annual_means_T(self):
        years = []
        values = []
        n = []
        for i in self.years:
            if i in self.T_ann_m:
                years.append(i)
                values.append(self.T_ann_m[i][0])
                n.append(self.T_ann_m[i][1])
            else:
                years.append(i)
                values.append("NA")
                n.append("NA")

        return [years, values, n]

    def reform_annual_means_P(self):
        years = []
        values = []
        n = []
        for i in self.years:
            if i in self.P_ann_m:
                years.append(i)
                values.append(self.P_ann_m[i][0])
                n.append(self.P_ann_m[i][1])
            else:
                years.append(i)
                values.append("NA")
                n.append("NA")

        return [years, values, n]


# For calculation of regression coefficients
class Reg:
    # t of form 'trio';  w --> perc., x --> O_18, y --> H_2
    def __init__(self, all_perc, t):
        self.n = len(t)

        self.x = [i[1] for i in t]
        self.y = [i[2] for i in t]

        self.s_x = sum(self.x)
        self.s_y = sum(self.y)

        self.s_x_sq = sum([i ** 2 for i in self.x])
        self.s_y_sq = sum([i ** 2 for i in self.y])
        self.m_x = self.s_x / self.n
        self.m_y = self.s_y / self.n

        self.U = [self.x[i] - self.m_x for i in range(self.n)]
        self.V = [self.y[i] - self.m_y for i in range(self.n)]
        self.s_U_sq = sum([self.U[i] ** 2 for i in range(self.n)])
        self.s_V_sq = sum([self.V[i] ** 2 for i in range(self.n)])
        self.s_UV = sum(self.U[i] * self.V[i] for i in range(self.n))

        # tuple -> (a,b)
        self.rma = self.RMA()
        self.rma_err = self.ERR(self.rma)
        self.ma = self.MA()
        self.ma_err = self.ERR(self.ma)

        # float
        self.r = self.R()


        if all_perc:
            w_sum = sum([i[0] for i in t])
            w = [i[0] / w_sum for i in t]
            x_w = [self.x[i] * w[i] for i in range(self.n)]
            y_w = [self.y[i] * w[i] for i in range(self.n)]
            s_x_w = sum(x_w)
            s_y_w = sum(y_w)

            Uw = [self.x[i] - s_x_w for i in range(self.n)]
            Vw = [self.y[i] - s_y_w for i in range(self.n)]
            s_Uw_sq = sum([w[i] * Uw[i] ** 2 for i in range(self.n)])
            s_Vw_sq = sum([w[i] * Vw[i] ** 2 for i in range(self.n)])
            s_UwVw = sum([w[i] * Uw[i] * Vw[i] for i in range(self.n)])

            # tuple -> (a,b)
            pwrma = self.PW_RMA(s_Vw_sq, s_Uw_sq, s_y_w, s_x_w)
            pwrma_err = self.PW_ERR(pwrma, w, s_Uw_sq)
            pwma = self.PW_MA(s_Vw_sq, s_Uw_sq, s_UwVw, s_y_w, s_x_w)
            pwma_err = self.PW_ERR(pwma, w, s_Uw_sq)

            # float
            pwr = self.PW_R(s_UwVw, s_Uw_sq, s_Vw_sq)
        else:
            w = 'NA'
            x_w = []
            y_w = []
            s_x_w = 'NA'
            s_y_w = 'NA'
            Uw = []
            Vw = []
            s_Uw_sq =  'NA'
            s_Vw_sq = 'NA'
            s_UwVw = 'NA'
            pwrma = ('NA''NA')
            pwrma_err = ('NA','NA')
            pwma = ('NA','NA')
            pwma_err = ('NA','NA')
            pwr = 'NA'

        self.w = w
        self.x_w = x_w
        self.y_w = y_w
        self.s_x_w = s_x_w
        self.s_y_w = s_y_w

        self.Uw = Uw
        self.Vw = Vw
        self.s_Uw_sq = s_Uw_sq
        self.s_Vw_sq = s_Vw_sq
        self.s_UwVw = s_UwVw

        self.pwrma = pwrma
        self.pwrma_err = pwrma_err
        self.pwma = pwma
        self.pwma_err = pwma_err

        self.pwr = pwr

    # reduced mayor axis regression
    def RMA(self):
        a = ((self.s_y_sq - self.s_y ** 2 / self.n) / (self.s_x_sq - self.s_x ** 2 / self.n)) ** 0.5
        b = self.m_y - a * self.m_x

        return (round(a, 2), round(b, 2))

    # precipitation weighted reduced mayor axis regression
    def PW_RMA(self, s_Vw_sq, s_Uw_sq, s_y_w, s_x_w):
        a = (s_Vw_sq / s_Uw_sq) ** 0.5
        b = s_y_w - a * s_x_w

        return (round(a, 2), round(b, 2))

    # mayor axis regression
    def MA(self):
        d = (self.s_V_sq - self.s_U_sq)
        a = (d + (d ** 2 + 4 * self.s_UV ** 2) ** 0.5) / (2 * self.s_UV)
        b = self.m_y - a * self.m_x

        return (round(a, 2), round(b, 2))

    # precipitation weighted mayor axis regression
    def PW_MA(self, s_Vw_sq, s_Uw_sq, s_UwVw, s_y_w, s_x_w):
        d = s_Vw_sq - s_Uw_sq
        a = (d + (d ** 2 + 4 * s_UwVw ** 2) ** 0.5) / (2 * s_UwVw)
        b = s_y_w - a * s_x_w

        return (round(a, 2), round(b, 2))

    # standard errors of parameters a and b for unweighted regression
    # par = 'parameters' - of form [a, b]
    def ERR(self, par):
        SE_a = (sum([(self.y[i] - (par[0] * self.x[i] + par[1])) ** 2 for i in range(self.n)]) / (
        self.n - 2)) ** 0.5 / self.s_U_sq ** 0.5
        SE_b = SE_a * (self.s_x_sq / self.n) ** 0.5

        return (round(SE_a, 2), round(SE_b, 2))

    # standard errors of parameters a and b for weighted regression
    # par = 'parameters' - of form [a, b]
    def PW_ERR(self, par, w, s_Uw_sq):
        SE_a = (self.n * sum([w[i] * (self.y[i] - (par[0] * self.x[i] + par[1])) ** 2 for i in range(self.n)]) / (
        self.n - 2)) ** 0.5 / (self.n * s_Uw_sq) ** 0.5
        SE_b = SE_a * (sum([w[i] * self.x[i] ** 2 for i in range(self.n)])) ** 0.5

        return (round(SE_a, 2), round(SE_b, 2))

    # pearson correlation coefficient
    def R(self):
        r = self.s_UV / (self.s_U_sq * self.s_V_sq) ** 0.5

        return round(r, 2)

    # weighted pearson correlation coefficient
    def PW_R(self, s_UwVw, s_Uw_sq, s_Vw_sq):
        r = s_UwVw / (s_Uw_sq * s_Vw_sq) ** 0.5

        return round(r, 2)

# For calculation of regression coeff. by years
def reg_by_years(tby):  # of form 'trio_by_years'
    o = {}  # list of objects
    for i, j in tby.items():
        if j != []:
            new_j = []
            filter_8_treshold = 0
            for k in j:
                if k[0] != 'NA':
                    new_j.append(k)
                    filter_8_treshold += 1
            if filter_8_treshold > 7:
                o[i] = Reg(True,new_j)

    return o


# ----- INITIATION OF OBJECTS -----------------------------------------------------------------------------------------

fajl = fajlname + koncnica

a = Proc('data/' + fajl)

O_18 = Stat(a.P_proc, a.O_18_proc, 2)
H_2 = Stat(a.P_proc, a.H_2_proc, 1)
d = Stat(a.P_proc, a.d_proc, 1)
H_3_TU = Stat(a.P_proc, a.H_3_TU_proc, 1)

PandT = PandTStat(a.P_proc,a.T_proc,a.year)

b = Reg(all_perc,a.trio)
o = reg_by_years(a.trio_by_y)


# ----- OFFLINE STATISTICS (writing in excel, graphs) -----------------------------------------------------------------

path = 'results/{}/'.format(fajlname)
if not os.path.isdir(path):
    os.makedirs(path)

if True:
    def means():
        name_of_file = "{}_{}".format("means", fajl)
        completeName = os.path.join(path, name_of_file)
        means = open(completeName, 'w')

        means.write("data type\tvalue\tn\t\n")
        means.write('O_18 \t' + str(O_18.m[0]) + '\t' + str(O_18.m[1]) + '\n')
        means.write('O_18 (w) \t' + str(O_18.w_m[0]) + '\t' + str(O_18.w_m[1]) + '\n')
        means.write('H_2 \t' + str(H_2.m[0]) + '\t' + str(H_2.m[1]) + '\n')
        means.write('H_2 (w) \t' + str(H_2.w_m[0]) + '\t' + str(H_2.w_m[1]) + '\n')
        means.write('d \t' + str(d.m[0]) + '\t' + str(d.m[1]) + '\n')
        means.write('d (w) \t' + str(d.w_m[0]) + '\t' + str(d.w_m[1]) + '\n')
        means.write('H_3_TU \t' + str(H_3_TU.m[0]) + '\t' + str(H_3_TU.m[1]) + '\n')
        means.write('H_3_TU (w) \t' + str(H_3_TU.w_m[0]) + '\t' + str(H_3_TU.w_m[1]) + '\n')
        means.write('T \t' + str(PandT.T_m[0]) + '\t' + str(PandT.T_m[1]) + '\n')
        means.write('P \t' + str(PandT.P_m[0]) + '\t' + str(PandT.P_m[1]) + '\n')

        means.close()

    # Assumption: there is no month for which there is no data
    def seasonal_means():
        name_of_file = "{}_{}".format("seasonal_means", fajl)
        completeName = os.path.join(path, name_of_file)
        seasonal_means = open(completeName, 'w')
        seasonal_means.write("data type\tspring\tn\tsummer\tn\tautumn\tn\t\winter\tn\t\n")

        seasonal_means.write('O_18\t')
        for i, j in O_18.sea_m.items():
            a = j[0]
            n = j[1]
            seasonal_means.write(str(a) + '\t' + str(n) + '\t')
        seasonal_means.write('\n')

        seasonal_means.write('H_2\t')
        for i, j in H_2.sea_m.items():
            a = j[0]
            n = j[1]
            seasonal_means.write(str(a) + '\t' + str(n) + '\t')
        seasonal_means.write('\n')

        seasonal_means.write('d\t')
        for i, j in d.sea_m.items():
            a = j[0]
            n = j[1]
            seasonal_means.write(str(a) + '\t' + str(n) + '\t')
        seasonal_means.write('\n')

        seasonal_means.write('H_3_TU\t')
        for i, j in H_3_TU.sea_m.items():
            a = j[0]
            n = j[1]
            seasonal_means.write(str(a) + '\t' + str(n) + '\t')
        seasonal_means.write('\n')

        seasonal_means.write('T\t')
        for i, j in PandT.T_sea_m.items():
            a = j[0]
            n = j[1]
            seasonal_means.write(str(a) + '\t' + str(n) + '\t')
        seasonal_means.write('\n')

        seasonal_means.write('P\t')
        for i, j in PandT.P_sea_m.items():
            a = j[0]
            n = j[1]
            seasonal_means.write(str(a) + '\t' + str(n) + '\t')
        seasonal_means.write('\n')

        seasonal_means.close()

    def weighted_seasonal_means():
        name_of_file = "{}_{}".format("weighted_seasonal_means", fajl)
        completeName = os.path.join(path, name_of_file)
        weighted_seasonal_means = open(completeName, 'w')
        weighted_seasonal_means.write("data type\tspring\tn\tsummer\tn\tautumn\tn\twinter\tn\t\n")

        weighted_seasonal_means.write('O_18\t')
        for i, j in O_18.w_sea_m.items():
            a = j[0]
            n = j[1]
            weighted_seasonal_means.write(str(a) + '\t' + str(n) + '\t')
        weighted_seasonal_means.write('\n')

        weighted_seasonal_means.write('H_2\t')
        for i, j in H_2.w_sea_m.items():
            a = j[0]
            n = j[1]
            weighted_seasonal_means.write(str(a) + '\t' + str(n) + '\t')
        weighted_seasonal_means.write('\n')

        weighted_seasonal_means.write('d\t')
        for i, j in d.w_sea_m.items():
            a = j[0]
            n = j[1]
            weighted_seasonal_means.write(str(a) + '\t' + str(n) + '\t')
        weighted_seasonal_means.write('\n')

        weighted_seasonal_means.write('H_3_TU\t')
        for i, j in H_3_TU.w_sea_m.items():
            a = j[0]
            n = j[1]
            weighted_seasonal_means.write(str(a) + '\t' + str(n) + '\t')
        weighted_seasonal_means.write('\n')

        weighted_seasonal_means.close()

    # Assumption: there is no month for which there is no data
    def monthly_means():
        name_of_file = "{}_{}".format("monthly_means", fajl)
        completeName = os.path.join(path, name_of_file)
        monthly_means = open(completeName, 'w')
        monthly_means.write("data type\t1\tn\t2\tn\t3\tn\t4\tn\t5\tn\t6\tn\t7\tn\t8\tn\t9\tn\t10\tn\t11\tn\t12\tn\t\n")

        monthly_means.write('O_18\t')
        for i, j in O_18.mon_m.items():
            a = j[0]
            n = j[1]
            monthly_means.write(str(a) + '\t' + str(n) + '\t')
        monthly_means.write('\n')

        monthly_means.write('H_2\t')
        for i, j in H_2.mon_m.items():
            a = j[0]
            n = j[1]
            monthly_means.write(str(a) + '\t' + str(n) + '\t')
        monthly_means.write('\n')

        monthly_means.write('d\t')
        for i, j in d.mon_m.items():
            a = j[0]
            n = j[1]
            monthly_means.write(str(a) + '\t' + str(n) + '\t')
        monthly_means.write('\n')

        monthly_means.write('H_3_TU\t')
        for i, j in H_3_TU.mon_m.items():
            a = j[0]
            n = j[1]
            monthly_means.write(str(a) + '\t' + str(n) + '\t')
        monthly_means.write('\n')

        monthly_means.write('T\t')
        for i, j in PandT.T_mon_m.items():
            a = j[0]
            n = j[1]
            monthly_means.write(str(a) + '\t' + str(n) + '\t')
        monthly_means.write('\n')

        monthly_means.write('P\t')
        for i, j in PandT.P_mon_m.items():
            a = j[0]
            n = j[1]
            monthly_means.write(str(a) + '\t' + str(n) + '\t')
        monthly_means.write('\n')

        monthly_means.close()

    def weighted_monthly_means():
        name_of_file = "{}_{}".format("weighted_monthly_means", fajl)
        completeName = os.path.join(path, name_of_file)
        weighted_monthly_means = open(completeName, 'w')
        weighted_monthly_means.write(
            "data type\t1\tn\t2\tn\t3\tn\t4\tn\t5\tn\t6\tn\t7\tn\t8\tn\t9\tn\t10\tn\t11\tn\t12\tn\t\n")

        weighted_monthly_means.write('O_18\t')
        for i, j in O_18.w_mon_m.items():
            a = j[0]
            n = j[1]
            weighted_monthly_means.write(str(a) + '\t' + str(n) + '\t')
        weighted_monthly_means.write('\n')

        weighted_monthly_means.write('H_2\t')
        for i, j in H_2.w_mon_m.items():
            a = j[0]
            n = j[1]
            weighted_monthly_means.write(str(a) + '\t' + str(n) + '\t')
        weighted_monthly_means.write('\n')

        weighted_monthly_means.write('d\t')
        for i, j in d.w_mon_m.items():
            a = j[0]
            n = j[1]
            weighted_monthly_means.write(str(a) + '\t' + str(n) + '\t')
        weighted_monthly_means.write('\n')

        weighted_monthly_means.write('H_3_TU\t')
        for i, j in H_3_TU.w_mon_m.items():
            a = j[0]
            n = j[1]
            weighted_monthly_means.write(str(a) + '\t' + str(n) + '\t')
        weighted_monthly_means.write('\n')

        weighted_monthly_means.close()

    def annual_means():
        global a
        name_of_file = "{}_{}".format("annual_means", fajl)
        completeName = os.path.join(path, name_of_file)
        annual_means = open(completeName, 'w')
        annual_means.write("data type\t")
        x = [i for i in a.year]
        y = []
        for i in x:
            if i not in y:
                y.append(i)

        for i in y:
            annual_means.write(str(i) + '\t' + 'n' + '\t')
        annual_means.write("\n")

        annual_means.write('O_18\t')
        for i in y:
            if i in O_18.ann_m.keys():
                annual_means.write(str(O_18.ann_m[i][0]) + '\t' + str(O_18.ann_m[i][1]) + '\t')
            else:
                annual_means.write('NA' + '\t' + 'NA' + '\t')
        annual_means.write('\n')

        annual_means.write('H_2\t')
        for i in y:
            if i in H_2.ann_m.keys():
                annual_means.write(str(H_2.ann_m[i][0]) + '\t' + str(H_2.ann_m[i][1]) + '\t')
            else:
                annual_means.write('NA' + '\t' + 'NA' + '\t')
        annual_means.write('\n')

        annual_means.write('d\t')
        for i in y:
            if i in d.ann_m.keys():
                annual_means.write(str(d.ann_m[i][0]) + '\t' + str(d.ann_m[i][1]) + '\t')
            else:
                annual_means.write('NA' + '\t' + 'NA' + '\t')
        annual_means.write('\n')

        annual_means.write('H_3_TU\t')
        for i in y:
            if i in H_3_TU.ann_m.keys():
                annual_means.write(str(H_3_TU.ann_m[i][0]) + '\t' + str(H_3_TU.ann_m[i][1]) + '\t')
            else:
                annual_means.write('NA' + '\t' + 'NA' + '\t')
        annual_means.write('\n')

        annual_means.write('T\t')
        for i in y:
            if i in PandT.T_ann_m.keys():
                annual_means.write(str(PandT.T_ann_m[i][0]) + '\t' + str(PandT.T_ann_m[i][1]) + '\t')
            else:
                annual_means.write('NA' + '\t' + 'NA' + '\t')
        annual_means.write('\n')

        annual_means.write('P\t')
        for i in y:
            if i in PandT.P_ann_m.keys():
                annual_means.write(str(PandT.P_ann_m[i][0]) + '\t' + str(PandT.P_ann_m[i][1]) + '\t')
            else:
                annual_means.write('NA' + '\t' + 'NA' + '\t')
        annual_means.write('\n')

        annual_means.close()

    def weighted_annual_means():
        global a
        name_of_file = "{}_{}".format("weighted_annual_means", fajl)
        completeName = os.path.join(path, name_of_file)
        weighted_annual_means = open(completeName, 'w')
        weighted_annual_means.write("data type\t")
        x = [i for i in a.year]
        y = []
        for i in x:
            if i not in y:
                y.append(i)

        for i in y:
            weighted_annual_means.write(str(i) + '\t' + 'n' + '\t')
        weighted_annual_means.write("\n")

        weighted_annual_means.write('O_18\t')
        for i in y:
            if i in O_18.w_ann_m.keys():
                weighted_annual_means.write(str(O_18.w_ann_m[i][0]) + '\t' + str(O_18.w_ann_m[i][1]) + '\t')
            else:
                weighted_annual_means.write('NA' + '\t' + 'NA' + '\t')
        weighted_annual_means.write('\n')

        weighted_annual_means.write('H_2\t')
        for i in y:
            if i in H_2.w_ann_m.keys():
                weighted_annual_means.write(str(H_2.w_ann_m[i][0]) + '\t' + str(H_2.w_ann_m[i][1]) + '\t')
            else:
                weighted_annual_means.write('NA' + '\t' + 'NA' + '\t')
        weighted_annual_means.write('\n')

        weighted_annual_means.write('d\t')
        for i in y:
            if i in d.w_ann_m.keys():
                weighted_annual_means.write(str(d.w_ann_m[i][0]) + '\t' + str(d.w_ann_m[i][1]) + '\t')
            else:
                weighted_annual_means.write('NA' + '\t' + 'NA' + '\t')
        weighted_annual_means.write('\n')

        weighted_annual_means.write('H_3_TU\t')
        for i in y:
            if i in H_3_TU.w_ann_m.keys():
                weighted_annual_means.write(str(H_3_TU.w_ann_m[i][0]) + '\t' + str(H_3_TU.w_ann_m[i][1]) + '\t')
            else:
                weighted_annual_means.write('NA' + '\t' + 'NA' + '\t')
        weighted_annual_means.write('\n')

        weighted_annual_means.close()


    def regression():
        name_of_file = "{}_{}".format("regression", fajl)
        completeName = os.path.join(path, name_of_file)
        regresija = open(completeName, 'w')
        regresija.write(
            'YEAR\tMETHOD\tSLOPE\tSLOPE ERROR\tINTERCEPT\tINTERCEPT ERROR\tPEARSON COEF.\tWEIGHTED PEARSON COEF.\tSAMPLE SIZE\t\n\n')
        regresija.write(
            '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t\n'.format('all', 'RMA', b.rma[0], b.rma_err[0], b.rma[1],
                                                                            b.rma_err[1], b.r, b.pwr, b.n) +
            '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t\n'.format('all', 'MA', b.ma[0], b.ma_err[0], b.ma[1],
                                                                            b.ma_err[1], '', '', '') +
            '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t\n'.format('all', 'PWRMA', b.pwrma[0], b.pwrma_err[0],
                                                                            b.pwrma[1], b.pwrma_err[1], '', '', '') +
            '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t\n'.format('all', 'PWMA', b.pwma[0], b.pwma_err[0],
                                                                            b.pwma[1], b.pwma_err[1], '', '', '') +
            '\n')
        for i, j in o.items():
            regresija.write(
                '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t\n'.format(i, 'RMA', j.rma[0], j.rma_err[0], j.rma[1],
                                                                                j.rma_err[1], j.r, j.pwr, j.n) +
                '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t\n'.format(i, 'MA', j.ma[0], j.ma_err[0], j.ma[1],
                                                                                j.ma_err[1], '', '', '') +
                '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t\n'.format(i, 'PWRMA', j.pwrma[0], b.pwrma_err[0],
                                                                                j.pwrma[1], j.pwrma_err[1], '', '', '') +
                '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t\n'.format(i, 'PWMA', j.pwma[0], j.pwma_err[0],
                                                                                j.pwma[1], j.pwma_err[1], '', '', '') +
                '\n')
        regresija.close()

    def reg_by_years_plot():
        y = []
        rma_slope = []
        rma_slope_err = []
        rma_intercept = []
        rma_intercept_err = []
        ma_slope = []
        ma_slope_err = []
        ma_intercept = []
        ma_intercept_err = []
        pwrma_slope = []
        pwrma_slope_err = []
        pwrma_intercept = []
        pwrma_intercept_err = []
        pwma_slope = []
        pwma_slope_err = []
        pwma_intercept = []
        pwma_intercept_err = []
        for i,j in o.items():
            y.append(int(i))
            rma_slope.append(j.rma[0])
            rma_slope_err.append(j.rma_err[0])
            rma_intercept.append(j.rma[1])
            rma_intercept_err.append(j.rma_err[1])
            ma_slope.append(j.ma[0])
            ma_slope_err.append(j.ma_err[0])
            ma_intercept.append(j.ma[1])
            ma_intercept_err.append(j.ma_err[1])
            pwrma_slope.append(j.pwrma[0])
            pwrma_slope_err.append(j.pwrma_err[0])
            pwrma_intercept.append(j.pwrma[1])
            pwrma_intercept_err.append(j.pwrma_err[1])
            pwma_slope.append(j.pwma[0])
            pwma_slope_err.append(j.pwma_err[0])
            pwma_intercept.append(j.pwma[1])
            pwma_intercept_err.append(j.pwma_err[1])

        return {"y" : y, "rma_slope" : rma_slope, "rma_slope_err" : rma_slope_err, "rma_intercept" : rma_intercept, "rma_intercept_err" : rma_intercept_err, "ma_slope" : ma_slope, "ma_slope_err" : ma_slope_err, "ma_intercept" : ma_intercept, "ma_intercept_err" : ma_intercept_err, "pwrma_slope" : pwrma_slope, "pwrma_slope_err" : pwrma_slope_err, "pwrma_intercept" : pwrma_intercept, "pwrma_intercept_err" : pwrma_intercept_err, "pwma_slope" : pwma_slope, "pwma_slope_err" : pwma_slope_err, "pwma_intercept" : pwma_intercept, "pwma_intercept_err" : pwma_intercept_err}

    # draw graphs of regression coeffs. changing over years
    def RegByYears(pd = reg_by_years_plot()):

        station_name = fajlname
        reg_path = path + 'regression_graphs/'
        if not os.path.isdir(reg_path):
            os.makedirs(reg_path)

        # --------------------------------------------------------------------------------------------------------------

        average = sum(pd["rma_slope"])/len(pd["y"])
        deviation = (sum([(pd["rma_slope"][i]-average)**2 for i in range(len(pd["y"]))])/(len(pd["y"])-1))**0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0]-0.5] + [i+0.5 for i in pd["y"]],[pd["rma_slope"][0]] + pd["rma_slope"],'r', linewidth = 1.2, label = 'data')
        t, = plt.step(pd["y"], [8 for i in range(len(pd["y"]))], 'm-', linewidth = 1.2, label = u"theoretic curve = 8")
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth = 1.2, label = u"average = {}".format(round(average,2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8, label = u"deviation = {}".format(round(deviation,2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8)
        plt.errorbar(pd["y"], pd["rma_slope"], yerr = pd["rma_slope_err"], fmt = 'None', ecolor='g', elinewidth = 0.8, capsize = 3)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr = [deviation for i in range(len(pd["y"]))], fmt = 'None', ecolor='c', elinewidth = 0.8, capsize = 0, capthick = 0.0)


        first_legend = plt.legend(handles=[rm,t,av,dev_up], loc=1)
        plt.title(station_name + ' RMA - slope')
        plt.xlabel('years')
        plt.ylabel('slope')
        plt.grid()
        plt.savefig(reg_path + station_name + ' RMA - slope', dpi=300)
        #plt.show()

        average = sum(pd["ma_slope"])/len(pd["y"])
        deviation = (sum([(pd["ma_slope"][i]-average)**2 for i in range(len(pd["y"]))])/(len(pd["y"])-1))**0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0]-0.5] + [i+0.5 for i in pd["y"]],[pd["ma_slope"][0]] + pd["ma_slope"],'r', linewidth = 1.2, label = 'data')
        t, = plt.step(pd["y"], [8 for i in range(len(pd["y"]))], 'm-', linewidth = 1.2, label = u"theoretic curve = 8")
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth = 1.2, label = u"average = {}".format(round(average,2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8, label = u"deviation = {}".format(round(deviation,2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8)
        plt.errorbar(pd["y"], pd["ma_slope"], yerr = pd["ma_slope_err"], fmt = 'None', ecolor='g', elinewidth = 0.8, capsize = 3)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr = [deviation for i in range(len(pd["y"]))], fmt = 'None', ecolor='c', elinewidth = 0.8, capsize = 0, capthick = 0.0)


        first_legend = plt.legend(handles=[rm,t,av,dev_up], loc=1)
        plt.title(station_name + ' MA - slope')
        plt.xlabel('years')
        plt.ylabel('slope')
        plt.grid()
        plt.savefig(reg_path + station_name + ' MA - slope', dpi=300)
        #plt.show()


        #--------------------------------------------------------------------------------------------------------------


        average = sum(pd["rma_intercept"])/len(pd["y"])
        deviation = (sum([(pd["rma_intercept"][i]-average)**2 for i in range(len(pd["y"]))])/(len(pd["y"])-1))**0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0]-0.5] + [i+0.5 for i in pd["y"]],[pd["rma_intercept"][0]] + pd["rma_intercept"],'r', linewidth = 1.2, label = 'data')
        t, = plt.step(pd["y"], [10 for i in range(len(pd["y"]))], 'm-', linewidth = 1.2, label = u"theoretic curve = 10‰")
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth = 1.2, label = u"average = {}‰".format(round(average,2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8, label = u"deviation = {}‰".format(round(deviation,2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8)
        plt.errorbar(pd["y"], pd["rma_intercept"], yerr = pd["rma_intercept_err"], fmt = 'None', ecolor='g', elinewidth = 0.8, capsize = 3)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr = [deviation for i in range(len(pd["y"]))], fmt = 'None', ecolor='c', elinewidth = 0.8, capsize = 0, capthick = 0.0)


        first_legend = plt.legend(handles=[rm,t,av,dev_up], loc=1)
        plt.title(station_name + ' RMA - intercept')
        plt.xlabel('years')
        plt.ylabel(u'intercept [‰]')
        plt.grid()
        plt.savefig(reg_path + station_name + ' RMA - intercept', dpi=300)
        #plt.show()

        average = sum(pd["ma_intercept"])/len(pd["y"])
        deviation = (sum([(pd["ma_intercept"][i]-average)**2 for i in range(len(pd["y"]))])/(len(pd["y"])-1))**0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0]-0.5] + [i+0.5 for i in pd["y"]],[pd["ma_intercept"][0]] + pd["ma_intercept"],'r', linewidth = 1.2, label = 'data')
        t, = plt.step(pd["y"], [10 for i in range(len(pd["y"]))], 'm-', linewidth = 1.2, label = u"theoretic curve = 10‰")
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth = 1.2, label = u"average = {}‰".format(round(average,2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8, label = u"deviation = {}‰".format(round(deviation,2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8)
        plt.errorbar(pd["y"], pd["ma_intercept"], yerr = pd["ma_intercept_err"], fmt = 'None', ecolor='g', elinewidth = 0.8, capsize = 3)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr = [deviation for i in range(len(pd["y"]))], fmt = 'None', ecolor='c', elinewidth = 0.8, capsize = 0, capthick = 0.0)


        first_legend = plt.legend(handles=[rm,t,av,dev_up], loc=1)
        plt.title(station_name + ' MA - intercept')
        plt.xlabel('years')
        plt.ylabel(u'intercept [‰]')
        plt.grid()
        plt.savefig(reg_path + station_name + ' MA - intercept', dpi=300)
        #plt.show()

        #----------------------------------------------------------------------------------------------------------------------

        average = sum(pd["pwrma_slope"]) / len(pd["y"])
        deviation = (sum([(pd["pwrma_slope"][i] - average) ** 2 for i in range(len(pd["y"]))]) / (len(pd["y"]) - 1)) ** 0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0] - 0.5] + [i + 0.5 for i in pd["y"]], [pd["pwrma_slope"][0]] + pd["pwrma_slope"], 'r',
                       linewidth=1.2, label='data')
        t, = plt.step(pd["y"], [8 for i in range(len(pd["y"]))], 'm-', linewidth=1.2, label=u"theoretic curve = 8")
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth=1.2,
                       label=u"average = {}".format(round(average, 2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth=0.8,
                           label=u"deviation = {}".format(round(deviation, 2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth=0.8)
        plt.errorbar(pd["y"], pd["pwrma_slope"], yerr=pd["pwrma_slope_err"], fmt='None', ecolor='g', elinewidth=0.8, capsize=3)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr=[deviation for i in range(len(pd["y"]))], fmt='None',
                     ecolor='c', elinewidth=0.8, capsize=0, capthick=0.0)

        first_legend = plt.legend(handles=[rm, t, av, dev_up], loc=1)
        plt.title(station_name + ' PWRMA - slope')
        plt.xlabel('years')
        plt.ylabel('slope')
        plt.grid()
        plt.savefig(reg_path + station_name + ' PWRMA - slope', dpi=300)
        #plt.show()

        average = sum(pd["pwma_slope"]) / len(pd["y"])
        deviation = (sum([(pd["pwma_slope"][i] - average) ** 2 for i in range(len(pd["y"]))]) / (len(pd["y"]) - 1)) ** 0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0] - 0.5] + [i + 0.5 for i in pd["y"]], [pd["pwma_slope"][0]] + pd["pwma_slope"], 'r',
                       linewidth=1.2, label='data')
        t, = plt.step(pd["y"], [8 for i in range(len(pd["y"]))], 'm-', linewidth=1.2, label=u"theoretic curve = 8")
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth=1.2,
                       label=u"average = {}".format(round(average, 2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth=0.8,
                           label=u"deviation = {}".format(round(deviation, 2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth=0.8)
        plt.errorbar(pd["y"], pd["pwma_slope"], yerr=pd["pwma_slope_err"], fmt='None', ecolor='g', elinewidth=0.8, capsize=3)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr=[deviation for i in range(len(pd["y"]))], fmt='None',
                     ecolor='c', elinewidth=0.8, capsize=0, capthick=0.0)

        first_legend = plt.legend(handles=[rm, t, av, dev_up], loc=1)
        plt.title(station_name + ' PWMA - slope')
        plt.xlabel('years')
        plt.ylabel('slope')
        plt.grid()
        plt.savefig(reg_path + station_name + ' PWMA - slope', dpi=300)
        #plt.show()

        #--------------------------------------------------------------------------------------------------------------

        average = sum(pd["pwrma_intercept"]) / len(pd["y"])
        deviation = (sum([(pd["pwrma_intercept"][i] - average) ** 2 for i in range(len(pd["y"]))]) / (len(pd["y"]) - 1)) ** 0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0] - 0.5] + [i + 0.5 for i in pd["y"]], [pd["pwrma_intercept"][0]] + pd["pwrma_intercept"], 'r',
                       linewidth=1.2, label='data')
        t, = plt.step(pd["y"], [10 for i in range(len(pd["y"]))], 'm-', linewidth=1.2, label=u"theoretic curve = 10‰")
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth=1.2,
                       label=u"average = {}‰".format(round(average, 2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth=0.8,
                           label=u"deviation = {}‰".format(round(deviation, 2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth=0.8)
        plt.errorbar(pd["y"], pd["pwrma_intercept"], yerr=pd["pwrma_intercept_err"], fmt='None', ecolor='g', elinewidth=0.8,
                     capsize=3)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr=[deviation for i in range(len(pd["y"]))], fmt='None',
                     ecolor='c', elinewidth=0.8, capsize=0, capthick=0.0)

        first_legend = plt.legend(handles=[rm, t, av, dev_up], loc=1)
        plt.title(station_name + ' PWRMA - intercept')
        plt.xlabel('years')
        plt.ylabel(u'intercept [‰]')
        plt.grid()
        plt.savefig(reg_path + station_name + ' PWRMA - intercept', dpi=300)
        #plt.show()

        average = sum(pd["pwma_intercept"]) / len(pd["y"])
        deviation = (sum([(pd["pwma_intercept"][i] - average) ** 2 for i in range(len(pd["y"]))]) / (len(pd["y"]) - 1)) ** 0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0] - 0.5] + [i + 0.5 for i in pd["y"]], [pd["pwma_intercept"][0]] + pd["pwma_intercept"], 'r',
                       linewidth=1.2, label='data')
        t, = plt.step(pd["y"], [10 for i in range(len(pd["y"]))], 'm-', linewidth=1.2, label=u"theoretic curve = 10‰")
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth=1.2,
                       label=u"average = {}‰".format(round(average, 2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth=0.8,
                           label=u"deviation = {}‰".format(round(deviation, 2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth=0.8)
        plt.errorbar(pd["y"], pd["pwma_intercept"], yerr=pd["pwma_intercept_err"], fmt='None', ecolor='g', elinewidth=0.8,
                     capsize=3)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr=[deviation for i in range(len(pd["y"]))], fmt='None',
                     ecolor='c', elinewidth=0.8, capsize=0, capthick=0.0)

        first_legend = plt.legend(handles=[rm, t, av, dev_up], loc=1)
        plt.title(station_name + ' PWMA - intercept')
        plt.xlabel('years')
        plt.ylabel(u'intercept [‰]')
        plt.grid()
        plt.savefig(reg_path + station_name + ' PWMA - intercept', dpi=300)
        #plt.show()

    # draw graphs that show the difference between different regression methods
    def RegByYears_diff(pd = reg_by_years_plot()):

        station_name = fajlname
        reg_path = path + 'regression_graphs/regression_graphs_of_differences/'
        if not os.path.isdir(reg_path):
            os.makedirs(reg_path)

        unweighted_slope_diff = np.asarray(pd["rma_slope"])-np.asarray(pd["ma_slope"])
        weighted_slope_diff = np.asarray(pd["pwrma_slope"])-np.asarray(pd["pwma_slope"])
        unweighted_intercept_diff = np.asarray(pd["rma_intercept"])-np.asarray(pd["ma_intercept"])
        weighted_intercept_diff = np.asarray(pd["pwrma_intercept"])-np.asarray(pd["pwma_intercept"])

        # --------------------------------------------------------------------------------------------------------------

        average = sum(unweighted_slope_diff)/len(pd["y"])
        deviation = (sum([(unweighted_slope_diff[i]-average)**2 for i in range(len(pd["y"]))])/(len(pd["y"])-1))**0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0]-0.5] + [i+0.5 for i in pd["y"]],np.concatenate(([unweighted_slope_diff[0]], unweighted_slope_diff)),'r', linewidth = 1.2, label = 'data')
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth = 1.2, label = u"average = {}".format(round(average,2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8, label = u"deviation = {}".format(round(deviation,2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr = [deviation for i in range(len(pd["y"]))], fmt = 'None', ecolor='c', elinewidth = 0.8, capsize = 0, capthick = 0.0)


        first_legend = plt.legend(handles=[rm,av,dev_up], loc=4)
        plt.title(station_name + ' (RMA-MA) - slope')
        plt.xlabel('years')
        plt.ylabel('slope')
        plt.grid()
        plt.savefig(reg_path + station_name + ' (RMA-MA) - slope', dpi=300)
        #plt.show()

        # --------------------------------------------------------------------------------------------------------------

        average = sum(unweighted_intercept_diff)/len(pd["y"])
        deviation = (sum([(unweighted_intercept_diff[i]-average)**2 for i in range(len(pd["y"]))])/(len(pd["y"])-1))**0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0]-0.5] + [i+0.5 for i in pd["y"]],np.concatenate(([unweighted_intercept_diff[0]], unweighted_intercept_diff)),'r', linewidth = 1.2, label = 'data')
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth = 1.2, label = u"average = {}".format(round(average,2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8, label = u"deviation = {}".format(round(deviation,2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr = [deviation for i in range(len(pd["y"]))], fmt = 'None', ecolor='c', elinewidth = 0.8, capsize = 0, capthick = 0.0)


        first_legend = plt.legend(handles=[rm,av,dev_up], loc=4)
        plt.title(station_name + ' (RMA-MA) - intercept')
        plt.xlabel('years')
        plt.ylabel('intercept')
        plt.grid()
        plt.savefig(reg_path + station_name + ' (RMA-MA) - intercept', dpi=300)
        #plt.show()

        # --------------------------------------------------------------------------------------------------------------

        average = sum(weighted_slope_diff)/len(pd["y"])
        deviation = (sum([(weighted_slope_diff[i]-average)**2 for i in range(len(pd["y"]))])/(len(pd["y"])-1))**0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0]-0.5] + [i+0.5 for i in pd["y"]],np.concatenate(([weighted_slope_diff[0]], weighted_slope_diff)),'r', linewidth = 1.2, label = 'data')
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth = 1.2, label = u"average = {}".format(round(average,2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8, label = u"deviation = {}".format(round(deviation,2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr = [deviation for i in range(len(pd["y"]))], fmt = 'None', ecolor='c', elinewidth = 0.8, capsize = 0, capthick = 0.0)


        first_legend = plt.legend(handles=[rm,av,dev_up], loc=4)
        plt.title(station_name + ' (PWRMA-PWMA) - slope')
        plt.xlabel('years')
        plt.ylabel('slope')
        plt.grid()
        plt.savefig(reg_path + station_name + ' (PWRMA-PWMA) - slope', dpi=300)
        #plt.show()

        # --------------------------------------------------------------------------------------------------------------

        average = sum(weighted_intercept_diff)/len(pd["y"])
        deviation = (sum([(weighted_intercept_diff[i]-average)**2 for i in range(len(pd["y"]))])/(len(pd["y"])-1))**0.5

        plt.figure(figsize=(16, 9))
        rm, = plt.step([pd["y"][0]-0.5] + [i+0.5 for i in pd["y"]],np.concatenate(([weighted_intercept_diff[0]], weighted_intercept_diff)),'r', linewidth = 1.2, label = 'data')
        av, = plt.step(pd["y"], [average for i in range(len(pd["y"]))], 'b-', linewidth = 1.2, label = u"average = {}".format(round(average,2)))
        dev_up, = plt.step(pd["y"], [average + deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8, label = u"deviation = {}".format(round(deviation,2)))
        dev_down, = plt.step(pd["y"], [average - deviation for i in range(len(pd["y"]))], 'c--', linewidth = 0.8)
        plt.errorbar(pd["y"], [average for i in range(len(pd["y"]))], yerr = [deviation for i in range(len(pd["y"]))], fmt = 'None', ecolor='c', elinewidth = 0.8, capsize = 0, capthick = 0.0)


        first_legend = plt.legend(handles=[rm,av,dev_up], loc=4)
        plt.title(station_name + ' (PWRMA-PWMA) - intercept')
        plt.xlabel('years')
        plt.ylabel('intercept')
        plt.grid()
        plt.savefig(reg_path + station_name + ' (PWRMA-PWMA) - intercept', dpi=300)
        #plt.show()

# ----- KLICANJE ZGORNJIH FUNKCIJ - odkomentiraj željene statistike ----------------------------------------------------

if input('All means? (y/n) ') == 'y':
    means()
if input('Seasonal means? (y/n) ') == 'y':
    seasonal_means()
if input('Precipitation weighted seasonal means? (y/n) ') == 'y':
    weighted_seasonal_means()
if input('Monthly means? (y/n) ') == 'y':
    monthly_means()
if input('Precipitation weighted monthy means? (y/n) ') == 'y':
    weighted_monthly_means()
if input('Annual means? (y/n) ') == 'y':
    annual_means()
if input('Precipitation weighted annual means? (y/n) ') == 'y':
    weighted_annual_means()
if input('Regression? (y/n) ') == 'y':
    print('...calculating...')
    regression()
if input('Regression by years? (y/n) ') == 'y':
    print('...calculating...')
    RegByYears()
    RegByYears_diff()
