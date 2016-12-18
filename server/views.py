from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from server.models import *
from server.forms import UserForm, MoveForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json

def index(request):
    return render(request, 'server/index.html', {})

def counterSession(request):
    # session counter
    if 'counter' in request.session:
        request.session['counter'] = request.session['counter'] + 1
        counterSes = request.session['counter']
    else:
        counterSes = 1
        request.session['counter'] = 1

    # global counter
    counterGlobal_db = Counter.objects.all().first()
    if counterGlobal_db:
    	counterGlobal_db.value = counterGlobal_db.value + 1
        counterGlobal_db.save()
        counterGlobal = counterGlobal_db.value
    else:
        counterGlobal_db_new = Counter(value=1)
        counterGlobal_db_new.save()
        counterGlobal = Counter.objects.all().first().value

    counter_variables = {
        'counterSes': counterSes,
        'counterGlobal': counterGlobal,
    }

    if request.is_ajax():
        template = "server/game_ajax.html"
    else:
        template = "server/game.html"

    return render(request, template, context=counter_variables)

def register_user(request):
    context_dict = {}
    registered = False

    if request.method == 'POST':

        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            registered = True

            context_dict["confirmation"] = "Your account has been created."
            return render(request, 'server/login.html', context_dict)

        else:
            print user_form.errors

    else:
        user_form = UserForm()

    return render(request, 'server/register.html', {'user_form': user_form, 'registered': registered})

def nologged(request):
    return render(request, 'server/nologged.html', {})

def login_user(request):
    context_dict = {}
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        gameType = request.POST.get('gameType')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                # Procesar si es Proprietary
                if gameType == 'proprietary':
                    create_game(request)
                    return HttpResponseRedirect('/server/game')
                else:
                    return HttpResponseRedirect('/server/wait')
                return HttpResponseRedirect('/server/login_user')
            else:
                context_dict["error"] = "Your gnuGame account is disabled."
                return render(request, 'server/login.html', context_dict)
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            context_dict["error"] = "Invalid login details supplied."
            return render(request, 'server/login.html', context_dict)

    else:
        return render(request, 'server/login.html', {})

@login_required
def logout_user(request):
    context_dict = {}

    context_dict["username"] = request.user.username

    logout(request)

    return HttpResponseRedirect('/server/index')

    return render(request, 'server/index.html', context_dict)

@login_required
def create_game(request):
    print "crea juego"
    context_dict = {}

    game=Game(proprietaryUser=request.user, gplUser=None)
    game.save()

    context_dict["game"] = game
    request.session['gameID'] = game.id
    request.session['amIproprietary'] = True

    return render(request, 'server/game.html', context_dict)

def clean_orphan_games(request):
    context_dict = {}

    games=Game.objects.filter(gplUser__isnull=True)
    for game in games:
        game.delete()

    context_dict["rows_count"] = len(games)

    return render(request, 'server/delete.html', context_dict)

@login_required
def join_game(request):
    context_dict = {}

    game_unico=Game.objects.filter(gplUser__isnull=True)
    if len(game_unico) > 0:
        tmpID = len(game_unico)-1
        game_asignado = Game.objects.get(id=game_unico[tmpID].id)
        game_asignado.gplUser = request.user
        game_asignado.save()

        request.session['gameID'] = game_unico[tmpID].id
        request.session['amIproprietary'] = False
        # Devolver datos al render
        context_dict["thereIsGame"] = True
        context_dict["thereIsGame_Ajax"] = 1
        context_dict["game"] = game_asignado
    else:
        # Devolver datos al render
        context_dict["thereIsGame"] = False
        context_dict["thereIsGame_Ajax"] = 0
        context_dict["error"] = "There are no games without users."

    # Devolve ajax
    if request.is_ajax():
        return HttpResponse(context_dict["thereIsGame_Ajax"])

@login_required
def proprietary_move(request, origin, target, game):
    context_dict = {}
    game = Game.objects.filter(id=game.id)
    if origin is None or target is None or game is None or len(game)<1:
        context_dict["error"] = "Movimiento no realizado: Hay un error con tu tablero."
    else:
        game = game[0]
        if game.proprietaryTurn == False:
            context_dict["error"] = "Movimiento no realizado: No es tu turno."
        else:
            if game.proprietary1 == origin or game.proprietary2 == origin or game.proprietary3 == origin or game.proprietary4 == origin:
                pass
            else:
                context_dict["error"] = "Movimiento no realizado: No hay ningun Proprietary en ese origen."
            if game.proprietary1 == target or game.proprietary2 == target or game.proprietary3 == target or game.proprietary4 == target or game.gpl == target:
                context_dict["error"] = "Movimiento no realizado: Ya existe un animal en esa casilla."
            else:
                # Continua aqui
                if target < origin:
                    context_dict["error"] = "Movimiento no realizado: Debes moverte en diagonal (hacia delante)."
                elif round(target/8) == round(origin/8):
                    context_dict["error"] = "Movimiento no realizado: No puedes mover sobre la misma fila."
                else:
                    check = (origin == (target - 7)) or (origin == (target - 9))
                    if check == True and target < 64:
                        move = Move(origin=origin, target=target, game=game)
                        if game.proprietary1 == origin:
                            game.proprietary1 = target
                        elif game.proprietary2 == origin:
                            game.proprietary2 = target
                        elif game.proprietary3 == origin:
                            game.proprietary3 = target
                        elif game.proprietary4 == origin:
                            game.proprietary4 = target

                        game.proprietaryTurn = False
                        move.save()
                        game.save()

                        context_dict["move"] = move
                        context_dict["game"] = game
                        context_dict["moveDone"] = True
                    else:
                        context_dict["error"] = "Movimiento no realizado: No puedes moverte a esa casilla."
    return context_dict

@login_required
def gpl_move(request, target, game):
    context_dict = {}
    game = Game.objects.filter(id=game.id)
    if target is None or game is None or len(game)<1:
        context_dict["error"] = "Movimiento no realizado: Hay un error con tu tablero."
    else:
        game = game[0]
        if game.proprietaryTurn == True:
            context_dict["error"] = "Movimiento no realizado: No es tu turno."
        elif round(target/8) == round(game.gpl/8):
            context_dict["error"] = "Movimiento no realizado: No puedes mover sobre la misma fila."
        else:
            # Continua aqui
            check = game.gpl == (target + 7) or game.gpl == (target + 9) or game.gpl == (target - 7) or game.gpl == (target - 9)
            if check == True and target < 64 and target >=0:
                move = Move(origin=game.gpl, target=target, game=game)

                game.gpl = target
                game.proprietaryTurn = True

                move.save()
                game.save()

                context_dict["move"] = move
                context_dict["game"] = game
                context_dict["moveDone"] = True
            else:
                context_dict["error"] = "Movimiento no realizado: No puedes moverte a esa casilla."
    return context_dict

@login_required
def move(request):

    moveDone = False
    gameID = None
    context_dict = {}
    response = None
    context_dict["error"] = None

    if request.method == 'POST':

        move_form = MoveForm(data=request.POST)

        if move_form.is_valid():
            origin = move_form.cleaned_data["origin"]
            target = move_form.cleaned_data["target"]

            if 'gameID' not in request.session or 'amIproprietary' not in request.session:
                context_dict["error"] = "Movimiento no realizado: Hay un error con tu tablero."
            else:
                gameID = request.session["gameID"]
                amIproprietary = request.session["amIproprietary"]
                game_object = Game.objects.filter(id=gameID)

                if len(game_object) > 0:
                    game_object = game_object[0]
                    if amIproprietary == True:
                        response = proprietary_move(request, origin, target, game_object)
                    elif amIproprietary == False:
                        response = gpl_move(request, target, game_object)

                    if 'error' in response:
                        context_dict["error"] = response["error"]

                    if 'moveDone' in response:
                        moveDone = True

                    if 'game' in response and 'move' in response:
                        context_dict["game"] = response["game"]
                        context_dict["move"] = response["move"]
                else:
                    context_dict["error"] = "Movimiento no realizado: Hay un error con tu tablero."

        else:
            print move_form.errors

    else:
        move_form = MoveForm()

    # Devolver formulario
    context_dict["move_form"] = move_form
    context_dict["moveDone"] = moveDone
    context_dict2 = {}
    context_dict2["moveDone"] = moveDone

    # Devolve ajax
    if request.is_ajax():
        if context_dict["error"] is not None:
            return HttpResponse('{"STATUS":0, "ERROR": "%s"}' % str(context_dict["error"]))
        else:
            return HttpResponse('{"STATUS":1, "ERROR": ""}')
    else:
        print context_dict
        return HttpResponse(json.dumps(context_dict2))

@login_required
def status_turn(request):
    context_dict = {}
    myTurn = False
    amIproprietary = request.session["amIproprietary"]
    game = Game.objects.filter(id=request.session["gameID"])
    game = game[0]
    if game.proprietaryTurn and amIproprietary:
        myTurn = True
    elif not game.proprietaryTurn and not amIproprietary:
        myTurn = True
    context_dict["myTurn"] = myTurn
    if request.is_ajax():
        return myTurn
    return render(request, 'server/turn.html', context_dict)

@login_required
def status_board(request):
    context_dict = {}

    if 'gameID' in request.session:

        game = Game.objects.filter(id=request.session["gameID"])

        if len(game) > 0:
            game = game[0]

            board = [0]*64
            board[game.proprietary1] = 1
            board[game.proprietary2] = 1
            board[game.proprietary3] = 1
            board[game.proprietary4] = 1

            board[game.gpl] = -1


            context_dict["board"] = board
            context_dict["myTurn"] = status_turn(request)
            context_dict["amIproprietary"] = request.session['amIproprietary']
            if context_dict["amIproprietary"] == True:
                context_dict["proprietary_opacity"] = "opacity: 1"
                context_dict["gpl_opacity"] = "opacity: 0.7"
            else:
                context_dict["proprietary_opacity"] = "opacity: 0.7"
                context_dict["gpl_opacity"] = "opacity: 1"

            if game.gplUser is None:
                context_dict["withoutCat"] = True
            else:
                context_dict["withoutCat"] = False

            context_dict["winnerCheck"] = check_winner(request)

    if request.is_ajax():
        template = "server/game_ajax.html"

    return render(request, template, context_dict)

@login_required
def game(request):
    context_dict = {}
    context_dict["username"] = request.user.username
    return render(request, 'server/game.html', context_dict)

def index(request):
    context_dict = {}
    context_dict["username"] = request.user.username
    return render(request, 'server/index.html', context_dict)

@login_required
def wait(request):
    context_dict = {}
    context_dict["username"] = request.user.username
    return render(request, 'server/wait.html', context_dict)

@login_required
def check_winner(request):
    winner = -1
    if 'gameID' in request.session:

        game = Game.objects.filter(id=request.session["gameID"])

        if len(game) > 0:
            game = game[0]

            # Gana GPL?
            proprietary1_pos = round((game.proprietary1/8)%8)
            proprietary2_pos = round((game.proprietary2/8)%8)
            proprietary3_pos = round((game.proprietary3/8)%8)
            proprietary4_pos = round((game.proprietary4/8)%8)

            gpl_pos = round((game.gpl/8)%8)

            if ((gpl_pos < proprietary1_pos) and (gpl_pos < proprietary2_pos) and (gpl_pos < proprietary3_pos) and (gpl_pos < proprietary4_pos)):
                return 0

            # Gana Proprietary?
            pos_arriba_izq = game.gpl - 9
            pos_arriba_der = game.gpl - 7
            pos_abajo_izq = game.gpl + 7
            pos_abajo_der = game.gpl + 9

            pos_arriba_izq_mod = round((pos_arriba_izq/8)%8)
            pos_arriba_der_mod = round((pos_arriba_der/8)%8)
            pos_abajo_izq_mod = round((pos_abajo_izq/8)%8)
            pos_abajo_der_mod = round((pos_abajo_der/8)%8)

            gpl_pos_mod = round((game.gpl/8)%8)

            proprietary_winner_status = False

            if (pos_arriba_izq_mod == gpl_pos_mod - 1):
                if(game.proprietary1==pos_arriba_izq)or(game.proprietary2==pos_arriba_izq)or(game.proprietary3==pos_arriba_izq)or(game.proprietary4==pos_arriba_izq):
                    proprietary_winner_status = True
                else:
                    return -1
            if (pos_arriba_der_mod == gpl_pos_mod - 1):
                if(game.proprietary1==pos_arriba_der)or(game.proprietary2==pos_arriba_der)or(game.proprietary3==pos_arriba_der)or(game.proprietary4==pos_arriba_der):
                    proprietary_winner_status = True
                else:
                    return -1
            if (pos_abajo_izq_mod == gpl_pos_mod + 1):
                if(game.proprietary1==pos_abajo_izq)or(game.proprietary2==pos_abajo_izq)or(game.proprietary3==pos_abajo_izq)or(game.proprietary4==pos_abajo_izq):
                    proprietary_winner_status = True
                else:
                    return -1
            if (pos_abajo_der_mod == gpl_pos_mod + 1):
                if(game.proprietary1==pos_abajo_der)or(game.proprietary2==pos_abajo_der)or(game.proprietary3==pos_abajo_der)or(game.proprietary4==pos_abajo_der):
                    proprietary_winner_status = True
                else:
                    return -1
            if proprietary_winner_status == True:
                return 1
    return -1

def show(request):
    context_dict = {}
    context_dict["username"] = request.user.username
    return render(request, "server/show.html", context_dict)
def show_ajax(request):
    context_dict = {}
    if Game.objects.count() > 0:
        game = Game.objects.latest('id')

        if game is not None:

            board = [0]*64
            board[game.proprietary1] = 1
            board[game.proprietary2] = 1
            board[game.proprietary3] = 1
            board[game.proprietary4] = 1

            board[game.gpl] = -1

            context_dict["game"] = game
            context_dict["board"] = board

    if request.is_ajax():
        template = "server/show_ajax.html"
    else:
        template = None

    return render(request, template, context_dict)
