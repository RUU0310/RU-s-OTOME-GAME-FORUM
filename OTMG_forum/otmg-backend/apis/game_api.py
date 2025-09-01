from flask import Blueprint, request, jsonify
from models import Game
from extension import db
from datetime import datetime
from models.game_user import GameUser
from models.user import User
from flask import session
from models.game_comment import GameComment
from models.game_comment_like import GameCommentLike
from models.game_character import GameCharacter
from models.group_post import Group, Post, PostFavorite, PostCategory
from models.group_post import GroupMember

game_bp = Blueprint('game', __name__)

# 你可以把原先的GameApi的所有方法拆成单独的函数
@game_bp.route('/games', methods=['GET'])
def get_games():
    # 获取查询参数
    status_filter = request.args.get('status')
    
    # 构建查询
    query = Game.query
    if status_filter:
        query = query.filter(Game.status == status_filter)
    
    games = query.all()
    results = [
        {
            'game_id': game.game_id,
            'name': game.name,
            'image_url': game.image_url,
            'description': game.description,
            'region': game.region,
            'publisher': game.publisher,
            'release_date': game.release_date.strftime('%Y-%m-%d') if game.release_date else None,
            'purchase_link': game.purchase_link,
            'is_official': game.is_official,
            'status': game.status,
            'created_at': game.created_at.strftime('%Y-%m-%d %H:%M:%S') if game.created_at else None,
        } for game in games
    ]
    return jsonify({'status': 'success', 'results': results})

@game_bp.route('/games', methods=['POST'])
def add_game():
    form = request.json
    game = Game(
        name=form.get('name'),
        image_url=form.get('image_url'),
        description=form.get('description'),
        region=form.get('region'),
        publisher=form.get('publisher'),
        release_date=datetime.strptime(form.get('release_date'), '%Y-%m-%d').date() if form.get('release_date') else None,
        purchase_link=form.get('purchase_link'),
        is_official=form.get('is_official', False),
        status='pending',  # 新添加的游戏默认为待审核状态
        created_at=datetime.utcnow()
    )
    db.session.add(game)
    db.session.commit()
    # 自动为新游戏创建小组（避免重复）
    if not Group.query.filter_by(game_id=game.game_id).first():
        group = Group(game_id=game.game_id, name=game.name + "小组", description=f"{game.name} 讨论小组")
        db.session.add(group)
        db.session.commit()
    return jsonify({'status': 'success', 'game_id': game.game_id})

@game_bp.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'status': 'error', 'message': '游戏不存在'}), 404
    form = request.json
    for field in ['name', 'image_url', 'description', 'region', 'publisher', 'purchase_link', 'is_official']:
        if field in form:
            setattr(game, field, form[field])
    # 单独处理 release_date
    if 'release_date' in form and form['release_date']:
        try:
            game.release_date = datetime.strptime(form['release_date'], '%Y-%m-%d').date()
        except Exception:
            return jsonify({'status': 'error', 'message': '日期格式错误'}), 400
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'status': 'error', 'message': '游戏不存在'}), 404
    db.session.delete(game)
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/games/<int:game_id>', methods=['GET'])
def get_game_detail(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'status': 'error', 'message': '游戏不存在'}), 404
    result = {
        'game_id': game.game_id,
        'name': game.name,
        'image_url': game.image_url,
        'description': game.description,
        'region': game.region,
        'publisher': game.publisher,
        'release_date': game.release_date.strftime('%Y-%m-%d') if game.release_date else None,
        'purchase_link': game.purchase_link,
        'is_official': game.is_official,
        'created_at': game.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(game, 'created_at') and game.created_at else None
    }
    return jsonify({'status': 'success', 'result': result})

@game_bp.route('/games/<int:game_id>/user_status', methods=['GET'])
def get_user_game_status(game_id):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'status': 'error', 'message': '缺少user_id'}), 400
    gu = GameUser.query.filter_by(user_id=user_id, game_id=game_id).first()
    if not gu:
        return jsonify({'status': 'success', 'result': None})
    return jsonify({'status': 'success', 'result': {'status': gu.status, 'rating': gu.rating}})

@game_bp.route('/games/<int:game_id>/user_status', methods=['POST'])
def set_user_game_status(game_id):
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '缺少user_id'}), 400
    status = data.get('status')
    rating = data.get('rating')
    gu = GameUser.query.filter_by(user_id=user_id, game_id=game_id).first()
    if not gu:
        gu = GameUser(user_id=user_id, game_id=game_id)
        db.session.add(gu)
    
    # 处理状态：如果status为None或空字符串，则清除状态
    if status is None or status == '':
        gu.status = None
    else:
        gu.status = status
    
    if rating is not None:
        if rating == '' or rating is None:
            gu.rating = None
        else:
            gu.rating = float(rating)
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/games/<int:game_id>/stats', methods=['GET'])
def get_game_stats(game_id):
    wish_count = GameUser.query.filter_by(game_id=game_id, status='wish').count()
    playing_count = GameUser.query.filter_by(game_id=game_id, status='playing').count()
    played_count = GameUser.query.filter_by(game_id=game_id, status='played').count()
    ratings = [gu.rating for gu in GameUser.query.filter(GameUser.game_id==game_id, GameUser.rating!=None).all()]
    avg_rating = round(sum(ratings)/len(ratings), 2) if ratings else None
    return jsonify({
        'status': 'success',
        'result': {
            'wish': wish_count,
            'playing': playing_count,
            'played': played_count,
            'avg_rating': avg_rating,
            'rating_count': len(ratings)
        }
    })

@game_bp.route('/games/<int:game_id>/comments', methods=['GET'])
def get_game_comments(game_id):
    user_id = request.args.get('user_id', type=int)
    comments = GameComment.query.filter_by(game_id=game_id).order_by(GameComment.created_at.desc()).all()
    result = []
    for c in comments:
        user = User.query.get(c.user_id)
        like_count = GameCommentLike.query.filter_by(comment_id=c.id).count()
        liked = False
        if user_id:
            liked = GameCommentLike.query.filter_by(comment_id=c.id, user_id=user_id).first() is not None
        # 获取评论用户对该游戏的评分
        user_game = GameUser.query.filter_by(user_id=c.user_id, game_id=game_id).first()
        user_rating = user_game.rating if user_game and user_game.rating else None
        result.append({
            'id': c.id,
            'user_id': c.user_id,
            'nickname': user.nickname if user else '',
            'avatar': user.avatar if user else '',
            'content': c.content,
            'created_at': c.created_at.isoformat() + 'Z' if c.created_at else None,
            'like_count': like_count,
            'liked': liked,
            'user_rating': user_rating,
            'user_role': user.role if user else 'user'
        })
    return jsonify({'status': 'success', 'results': result})

@game_bp.route('/games/<int:game_id>/comments', methods=['POST'])
def add_game_comment(game_id):
    data = request.json
    user_id = data.get('user_id')
    content = data.get('content', '').strip()
    if not user_id or not content:
        return jsonify({'status': 'error', 'message': '缺少用户或内容'}), 400
    comment = GameComment(game_id=game_id, user_id=user_id, content=content)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/games/<int:game_id>/comments/<int:comment_id>/like', methods=['POST'])
def like_game_comment(game_id, comment_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '缺少user_id'}), 400
    like = GameCommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        liked = False
    else:
        db.session.add(GameCommentLike(user_id=user_id, comment_id=comment_id))
        db.session.commit()
        liked = True
    like_count = GameCommentLike.query.filter_by(comment_id=comment_id).count()
    return jsonify({'status': 'success', 'like_count': like_count, 'liked': liked})

@game_bp.route('/games/<int:game_id>/comments/<int:comment_id>', methods=['PUT'])
def edit_game_comment(game_id, comment_id):
    data = request.json
    user_id = data.get('user_id')
    content = data.get('content', '').strip()
    comment = GameComment.query.filter_by(id=comment_id, game_id=game_id, user_id=user_id).first()
    if not comment:
        return jsonify({'status': 'error', 'message': '评论不存在或无权限'}), 403
    if not content:
        return jsonify({'status': 'error', 'message': '内容不能为空'}), 400
    comment.content = content
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/games/<int:game_id>/comments/<int:comment_id>', methods=['DELETE'])
def delete_game_comment(game_id, comment_id):
    user_id = request.args.get('user_id', type=int)
    comment = GameComment.query.filter_by(id=comment_id, game_id=game_id, user_id=user_id).first()
    if not comment:
        return jsonify({'status': 'error', 'message': '评论不存在或无权限'}), 403
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'status': 'success'})

# 角色：增
@game_bp.route('/games/<int:game_id>/characters', methods=['POST'])
def add_character(game_id):
    data = request.json
    char = GameCharacter(
        game_id=game_id,
        name=data.get('name'),
        cv=data.get('cv'),
        avatar=data.get('avatar'),
        description=data.get('description'),
        extra_info=data.get('extra_info'),
        role_type=data.get('role_type', '可攻略')
    )
    db.session.add(char)
    db.session.commit()
    return jsonify({'status': 'success', 'id': char.id})

# 角色：查（列表）
@game_bp.route('/games/<int:game_id>/characters', methods=['GET'])
def get_characters(game_id):
    chars = GameCharacter.query.filter_by(game_id=game_id).all()
    results = []
    for c in chars:
        results.append({
            'id': c.id,
            'game_id': c.game_id,
            'name': c.name,
            'cv': c.cv,
            'avatar': c.avatar,
            'description': c.description,
            'extra_info': c.extra_info,
            'role_type': c.role_type
        })
    return jsonify({'status': 'success', 'results': results})

# 角色：查（单个）
@game_bp.route('/characters/<int:char_id>', methods=['GET'])
def get_character(char_id):
    c = GameCharacter.query.get(char_id)
    if not c:
        return jsonify({'status': 'error', 'message': '角色不存在'}), 404
    return jsonify({'status': 'success', 'result': {
        'id': c.id,
        'game_id': c.game_id,
        'name': c.name,
        'cv': c.cv,
        'avatar': c.avatar,
        'description': c.description,
        'extra_info': c.extra_info,
        'role_type': c.role_type
    }})

# 角色：改
@game_bp.route('/characters/<int:char_id>', methods=['PUT'])
def update_character(char_id):
    c = GameCharacter.query.get(char_id)
    if not c:
        return jsonify({'status': 'error', 'message': '角色不存在'}), 404
    data = request.json
    for field in ['name', 'cv', 'avatar', 'description', 'extra_info', 'role_type']:
        if field in data:
            setattr(c, field, data[field])
    db.session.commit()
    return jsonify({'status': 'success'})

# 角色：删
@game_bp.route('/characters/<int:char_id>', methods=['DELETE'])
def delete_character(char_id):
    c = GameCharacter.query.get(char_id)
    if not c:
        return jsonify({'status': 'error', 'message': '角色不存在'}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({'status': 'success'})

@game_bp.route('/users/<int:user_id>/game-status', methods=['GET'])
def get_user_game_status_list(user_id):
    """获取用户的所有游戏状态"""
    try:
        # 获取用户的所有游戏状态
        game_users = GameUser.query.filter_by(user_id=user_id).all()
        
        # 获取所有游戏信息
        games = Game.query.all()
        game_map = {game.game_id: game for game in games}
        
        # 按状态分类
        wish_games = []
        playing_games = []
        played_games = []
        
        for gu in game_users:
            game = game_map.get(gu.game_id)
            if not game:
                continue
                
            game_info = {
                'game_id': game.game_id,
                'name': game.name,
                'image_url': game.image_url,
                'publisher': game.publisher,
                'rating': gu.rating
            }
            
            if gu.status == 'wish':
                wish_games.append(game_info)
            elif gu.status == 'playing':
                playing_games.append(game_info)
            elif gu.status == 'played':
                played_games.append(game_info)
        
        return jsonify({
            'status': 'success',
            'game_status': {
                'wish': wish_games,
                'playing': playing_games,
                'played': played_games
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@game_bp.route('/users/<int:user_id>/favorite-posts', methods=['GET'])
def get_user_favorite_posts(user_id):
    """获取用户收藏的帖子"""
    try:
        # 获取用户收藏的帖子
        favorites = PostFavorite.query.filter_by(user_id=user_id).all()
        
        favorite_posts = []
        for fav in favorites:
            post = Post.query.get(fav.post_id)
            if not post:
                continue
                
            # 获取分类信息
            category_name = None
            if post.category_id:
                category = PostCategory.query.get(post.category_id)
                category_name = category.name if category else None
            
            # 获取点赞数
            from models.group_post import PostLike
            like_count = PostLike.query.filter_by(post_id=post.post_id).count()
            
            # 获取用户信息
            user = User.query.get(post.user_id)
            username = user.username if user else None
            nickname = user.nickname if user else None
            
            # 获取小组信息
            group = Group.query.get(post.group_id)
            group_name = group.name if group else None
            
            post_data = {
                'post_id': post.post_id,
                'group_id': post.group_id,
                'group_name': group_name,
                'user_id': post.user_id,
                'username': username,
                'nickname': nickname,
                'title': post.title,
                'content': post.content,
                'images': post.images,
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M') if post.created_at else None,
                'updated_at': post.updated_at.strftime('%Y-%m-%d %H:%M') if post.updated_at else None,
                'category_id': post.category_id,
                'category_name': category_name,
                'is_poll': post.is_poll,
                'poll_type': post.poll_type,
                'poll_deadline': post.poll_deadline,
                'like_count': like_count,
                'favorite_time': fav.created_at.strftime('%Y-%m-%d %H:%M') if fav.created_at else None
            }
            favorite_posts.append(post_data)
        
        # 按收藏时间倒序排列
        favorite_posts.sort(key=lambda x: x['favorite_time'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'favorite_posts': favorite_posts
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 游戏审核相关API
@game_bp.route('/games/audit', methods=['GET'])
def get_games_for_audit():
    """获取待审核的游戏列表"""
    try:
        status_filter = request.args.get('status', 'pending')
        games = Game.query.filter_by(status=status_filter).order_by(Game.created_at.desc()).all()
        
        results = []
        for game in games:
            results.append({
                'game_id': game.game_id,
                'name': game.name,
                'image_url': game.image_url,
                'description': game.description,
                'region': game.region,
                'publisher': game.publisher,
                'release_date': game.release_date.strftime('%Y-%m-%d') if game.release_date else None,
                'purchase_link': game.purchase_link,
                'is_official': game.is_official,
                'status': game.status,
                'created_at': game.created_at.strftime('%Y-%m-%d %H:%M:%S') if game.created_at else None,
            })
        
        return jsonify({'status': 'success', 'results': results})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@game_bp.route('/games/<int:game_id>/audit', methods=['PUT'])
def audit_game(game_id):
    """审核游戏"""
    try:
        data = request.json
        new_status = data.get('status')
        reason = data.get('reason', '')
        
        if new_status not in ['approved', 'rejected']:
            return jsonify({'status': 'error', 'message': '无效的审核状态'}), 400
        
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'status': 'error', 'message': '游戏不存在'}), 404
        
        game.status = new_status
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'游戏已{new_status == "approved" and "通过" or "拒绝"}审核'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500