from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
import pymysql
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from arigonggan import models
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
sched = BackgroundScheduler()
import datetime
now = datetime.datetime.now()
import time

@sched.scheduled_job('cron', hour='09', minute='00', name='disable1')
def seatChangeDisable():
    stime = "09:00:00"
    models.updateSeatDisable(stime)
    print(stime + " disable complete")

@sched.scheduled_job('cron', hour='10', minute='00', name='disable2')
def seatChangeDisable():
    stime = "10:00:00"
    models.updateSeatDisable(stime)
    print(stime + " disable complete")

@sched.scheduled_job('cron', hour='11', minute='00', name='disable3')
def seatChangeDisable():
    stime = "11:00:00"
    models.updateSeatDisable(stime)
    print(stime + " disable complete")

@sched.scheduled_job('cron', hour='12', minute='00', name='disable4')
def seatChangeDisable():
    stime = "12:00:00"
    models.updateSeatDisable(stime)
    print(stime + " disable complete")

@sched.scheduled_job('cron', hour='13', minute='00', name='disable5')
def seatChangeDisable():
    stime = "13:00:00"
    models.updateSeatDisable(stime)
    print("disable complete" + stime)


@sched.scheduled_job('cron', hour='14', minute='00', name='disable6')
def seatChangeDisable():
    stime = "14:00:00"
    models.updateSeatDisable(stime)
    print("disable complete" + stime)


@sched.scheduled_job('cron', hour='15', minute='00', name='disable7')
def seatChangeDisable():
    stime = "15:00:00"
    models.updateSeatDisable(stime)
    print("disable complete" + stime)


@sched.scheduled_job('cron', hour='16', minute='00', name='disable8')
def seatChangeDisable():
    stime = "16:00:00"
    models.updateSeatDisable(stime)
    print("disable complete" + stime)


@sched.scheduled_job('cron', hour='17', minute='00', name='disable9')
def seatChangeDisable():
    stime = "17:00:00"
    models.updateSeatDisable(stime)
    print("disable complete" + stime)



@sched.scheduled_job('cron', hour='18', minute='00', name='disable10')
def seatChangeDisable():
    stime = "18:00:00"
    models.updateSeatDisable(stime)
    print("disable complete" + stime)

sched.start()

@sched.scheduled_job('cron',hour='00', minute = '00', name = 'activate')
def seatChangeActivate():
    models.updateAllSeatActivate()
    print("activate complete")

def signup(userId):
    res = models.userInsert(userId)
    return 0

# (00) session check api
@method_decorator(csrf_exempt,name='dispatch')
def index(request):
    if request.method == 'GET':
        userId = request.session.get('userId')
        return HttpResponse(userId)

# (01) signUp & signIn api
@method_decorator(csrf_exempt,name='dispatch')
def logIn(requset):
    if requset.method == 'POST':
        try:
            data = json.loads(requset.body)
            userId = data['userId']

            # 로그인 전적이 있는 지 확인
            res = models.selectUser(userId)
            if (res==None):
                # 회원가입
                signup(userId)
            # session에 userId 추가
            requset.session['userId'] = userId
        except:
            return JsonResponse({'message':'DB_ERR'},status=400)
        return JsonResponse({'message': 'SUCCESS'}, status=200)

# (02) signOut api
    elif requset.method == 'PATCH':
        try:
            del requset.session['userId']
            return JsonResponse({'message':'SUCCESS'},status=200)
        except: return JsonResponse({'message':'WRONG_User'},status=300)

# (03) add Reservation api
@method_decorator(csrf_exempt,name='dispatch')
def reservation(request):
    if request.method == 'POST':

        # Login Check
        userId = request.session.get('userId')
        if userId=="None":
            return JsonResponse({'message':'WRONG_User'},status=300)
        else:
            data = json.loads(request.body)
            floor = data['floor']
            name = data['name']
            time = data['time']
            scheTIme = str(int(time[0:2])-1)
            seatInfoQuery = (floor,name,time)
            try:
                seat = models.retrieveAvailavleSeat(seatInfoQuery)
                if (seat!=None):
                    models.updateSeatStatus(seat[0])
                    reservationQuery = (userId,seat[0],"deactivation")
                    models.insertReservation(reservationQuery)
                    if(int(time[0:2])==now.hour):
                        infoQuery = ('prebooked', 'deactivation', seat[0], userId)
                        models.updateReservation(infoQuery)
                        scheTIme = now.hour
                        @sched.scheduled_job('cron', year=now.year, month=now.month, day=now.day, hour=scheTIme,minute="10")
                        def seatChangeCanceled():
                            reserveIdQuery = (userId, seat[0], 'prebooked')
                            reserveId = models.retrieveReserveId(reserveIdQuery)
                            if (len(reserveId) != 0):
                                models.autoDelete(reserveId[0])
                    elif(int(scheTIme)==now and now.minute >= 50):
                        infoQuery = ('prebooked', 'deactivation', seat[0], userId)
                        models.updateReservation(infoQuery)
                        scheTIme = int(scheTIme) + 1
                        @sched.scheduled_job('cron', year=now.year, month=now.month, day=now.day, hour=scheTIme,minute="10")
                        def seatChangeCanceled():
                            reserveIdQuery = (userId, seat[0], 'prebooked')
                            reserveId = models.retrieveReserveId(reserveIdQuery)
                            if (len(reserveId) != 0):
                                models.autoDelete(reserveId[0])
                    else:
                        @sched.scheduled_job('cron',year=now.year,month=now.month,day=now.day,hour=scheTIme,minute="50")
                        def seatChangePrebooked():
                            infoQuery = ('prebooked','deactivation',seat[0],userId)
                            models.updateReservation(infoQuery)
                        @sched.scheduled_job('cron', year=now.year, month=now.month, day=now.day, hour=time[0:2],minute="10")
                        def seatChangeCanceled():
                            reserveIdQuery = (userId, seat[0], 'prebooked')
                            reserveId = models.retrieveReserveId(reserveIdQuery)
                            if (len(reserveId) != 0):
                                models.autoDelete(reserveId[0])
                    return JsonResponse({'message': 'SUCCESS'}, status=200)
                else:   return JsonResponse({'message':'이미 예약된 자석 이거나 현재 사용 불가한 자석입니다.'},status=200)
            except: return JsonResponse({'message':'DB_ERR'},status=400)

# (04) retrieve all seat status
@method_decorator(csrf_exempt,name='dispatch')
def seatList(requset):
    try:
        res = models.retrieveAllSeatStatus()
        return JsonResponse({'message': 'SUCCESS','res':res}, status=200)
    except: return JsonResponse({'message':'DB_ERR'},status=400)

# (05) delete Reservation api
@method_decorator(csrf_exempt, name='dispatch')
def delete(request):
    userId = request.session.get('userId')
    if userId==None:
        return JsonResponse({'message':'WRONG_User'},status=300)
    else:
        data = json.loads(request.body)
        floor = data['floor']
        name = data['name']
        time = data['time']
        seatInfo = (floor,name,time)
        try:
            seat = models.retrieveSeatId(seatInfo)
            ReserveInfoQuery = (userId,seat[0])
            reserveId = models.retrievedeleteId(ReserveInfoQuery)
            if reserveId == None:
                return JsonResponse({'message': 'Wrong reservation'}, status=301)
            else:
                models.deleteReservation(reserveId[0])
                models.deleteSeatStatus(seat[0])
                return JsonResponse({'message': 'SUCCESS'}, status=200)
        except:
            return JsonResponse({'message': 'DBERR'}, status=400)

# (06) auto delete Reservation api
@method_decorator(csrf_exempt, name='dispatch')
def autoDelete(request):

    data = json.loads(request.body)
    userId = data['userId']
    floor = data['floor']
    name = data['name']
    time = data['time']
    try:
        queryInfo = (floor, name, time)
        seat = models.retrieveSeatId(queryInfo)
        ReserveInfoQuery = (userId, seat[0])
        reserveId = models.retrievedeleteId(ReserveInfoQuery)
        if reserveId == None:
            return JsonResponse({'message': 'Wrong reservation'}, status=300)
        else:
            models.autoDelete(reserveId[0])
            models.deleteSeatStatus(seat[0])
            return JsonResponse({'message': 'SUCCESS'}, status=200)
    except:
        return JsonResponse({'message': 'DBERR'}, status=400)

# (07) Retrieve User Reservation List
@method_decorator(csrf_exempt, name='dispatch')
def userReservation(request):
    userId = request.session.get('userId')
    if userId==None:
        return JsonResponse({'message':'WRONG_User'},status=300)
    else:
        try:
            reservationList = models.retrieveReserv(userId)
            if len(reservationList) == 0:
                return JsonResponse({'message': '예약 내역이 없습니다'}, status=200)
            else:
                resLIst = []
                i=0
                for item in reservationList:
                    seatInfo = models.retrieveSeatById(reservationList[i][0])
                    tmp = (reservationList[i]+seatInfo)[1:]
                    i+=1;
                    resLIst.append(tmp)
                return JsonResponse({'message': 'SUCCESS','res':resLIst}, status=200)
        except:
            return JsonResponse({'message': 'DBERR'}, status=400)

# (06) auto delete Reservation api
@method_decorator(csrf_exempt, name='dispatch')
def booked(request):
    data = json.loads(request.body)
    userId = request.session.get('userId')
    floor = data['floor']
    name = data['name']
    time = data['time']

    if userId==None:
        return JsonResponse({'message':'WRONG_User'},status=300)

    try:
        info = (floor,name,time)
        seat = models.retrieveSeatId(info)
        ReserveInfoQuery = (userId, seat[0],'prebooked')
        reserveId = models.retrieveReserveId(ReserveInfoQuery)
        if reserveId == None:
            return JsonResponse({'message': 'Wrong reservation'}, status=301)
        else:
            reserveInfo = ('booked','prebooked',seat[0],userId)
            models.updateReservation(reserveInfo)

            return JsonResponse({'message': 'SUCCESS'}, status=200)
    except:
        return JsonResponse({'message': 'DBERR'}, status=400)

# (06) auto delete Reservation api
@method_decorator(csrf_exempt, name='dispatch')
def reserveList(request):

    data = json.loads(request.body)
    userId = request.session.get('userId')
    if userId==None:
        return JsonResponse({'message':'WRONG_User'},status=300)
    try:
        seats = models.checkChangeList(userId)
        return JsonResponse({'message': 'SUCCESS','res' : seats}, status=200)
    except:
        return JsonResponse({'message': 'DBERR'}, status=400)


# (07) disalble seat
@method_decorator(csrf_exempt, name='dispatch')
def disableSeat(request):
    try:
        models.updateAllSeatDisable()
        res = models.retrieveAllSeatStatus()
        return JsonResponse({'message': 'SUCCESS','res':res}, status=200)
    except:
        return JsonResponse({'message': 'DBERR'}, status=400)

# (08) activate seat
@method_decorator(csrf_exempt, name='dispatch')
def activateSeat(request):
    try:
        models.updateAllSeatActivate()
        res = models.retrieveAllSeatStatus()
        return JsonResponse({'message': 'SUCCESS','res':res}, status=200)
    except:
        return JsonResponse({'message': 'DBERR'}, status=400)