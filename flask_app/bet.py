from sqlalchemy import func
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, jsonify
from models import db, Bets

bet_api_blueprint = Blueprint('bet_api', __name__)

@bet_api_blueprint.route("/bet-summary", methods=["GET"])
@jwt_required()
def get_bet_summary():
    user_id = int(get_jwt_identity())
    print(f"✅ get_bet_summary: user_id = {user_id}")
    
    results = db.session.query(
        Bets.date_info,
        func.sum(Bets.amount).label('total_amount')
    ).filter(Bets.user_id == user_id).group_by(Bets.date_info).all()

    print(f"✅ get_bet_summary: results = {results}")
    
    data = [{"date_info": r[0], "total_amount": float(r[1])} for r in results]
    return jsonify(data)
