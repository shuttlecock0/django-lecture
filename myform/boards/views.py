from django.shortcuts import render, redirect, get_object_or_404
from IPython import embed
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Board, Comment
from .forms import BoardForm, CommentForm
from django.utils import timezone

# Create your views here.
def index(request):
    boards = Board.objects.order_by('-pk')
    context = {'boards': boards}
    return render(request, 'boards/index.html', context)

@login_required
def create(request):
    if request.method == 'POST':
        # Data Binding form 인스턴스 생성하고 (request.POST)로 데이터를 채운다. 
        form = BoardForm(request.POST)
        # form 유효성 체크
        if form.is_valid():
            # 1방법
            # # cleaned_data는 queryDict를 return하기 때문에 .get으로 접근 가능
            # title = form.cleaned_data.get('title')
            # content = form.cleaned_data.get('content')
            # # 검증을 통과한 깨끗한 데이터를 form에서 가져와 board 인스턴스를 만든다.
            # board = Board.objects.create(title=title, content=content)

            # 2방법
            board = form.save(commit=False)
            board.user = request.user
            board.save()
            return redirect('boards:detail', board.pk)
    # GET일 때는 기본 form 인스턴스를 생성
    else:
        form = BoardForm()
    # GET 방식은 기본 form 모습으로 넘겨짐
    # POST 요청에서 검증에 실패하면 오류메시지를 포함한 상태로 넘겨짐
    context = {'form': form }
    return render(request, 'boards/form.html', context)

def detail(request, board_pk):
    # board = Board.objects.get(pk=board_pk)
    board = get_object_or_404(Board, pk=board_pk)
    comments = board.comment_set.all()
    comment_form = CommentForm()
    person = get_object_or_404(get_user_model(), pk=board.user.pk)
    context = {
        'board':board,
        'comment_form': comment_form,
        'comments': comments,
        'person': person,
    }
    return render(request, 'boards/detail.html', context)

def delete(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    if board.user == request.user:
        if request.method == 'POST':
            board.delete()
            return redirect('boards:index')
        else:
            return redirect('boards:detail', board.pk)
    else:
        return redirect('boards:index')

@login_required
def update(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    if board.user == request.user:
        if request.method == 'POST':
            form = BoardForm(request.POST, instance=board)
            if form.is_valid():
                # 1방법
                # board.title = form.cleaned_data.get('title')
                # board.content = form.cleaned_data.get('content')
                # board.save()

                # 2방법
                board = form.save(commit=False)
                board.updated_at = timezone.now()
                board.save()
                return redirect('boards:detail', board.pk)
        else:
            form = BoardForm(initial=board.__dict__)
    else:
        return redirect('boards:index')
    context = {
        'form': form,
        'board': board,
    }
    return render(request, 'boards/form.html', context)

# 로그인 된 유저만 작성 가능
# POST로만 작성
@login_required
@require_POST

def comments_create(request, board_pk):
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.user = request.user
        comment.board_id = board_pk 
        comment.save()
    return redirect('boards:detail', board_pk)

@login_required
@require_POST
def comments_delete(request, board_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if comment.user == request.user:
        comment.delete()
    return redirect('boards:detail', board_pk)

@require_POST # 405
@login_required
def like(request, board_pk):
    if request.is_ajax():
        board = get_object_or_404(Board, pk=board_pk)
        user = request.user
        if board.like_users.filter(pk=user.pk).exists():
        # if user in board.like_users.all(): 위랑 같은 의미이지만 cache를 남겨서 최적화에 적합하지 않음
            board.like_users.remove(user)
            liked = False
        else:
            board.like_users.add(user)
            liked = True
        context = {
            'liked': liked, 
            'count': board.like_users.count(),
        }
        return JsonResponse(context)
    else:
        return HttpResponseBadRequest()

def follow(request, user_pk):
    person = get_object_or_404(get_user_model(), pk=user_pk)
    user = request.user
    if person.followers.filter(pk=user.pk).exists():
        person.followers.remove(user)
    else:
        person.followers.add(user)
    return redirect('profile', person.username)