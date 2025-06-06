from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User, bcrypt


@app.route("/api/user/bet-summary", methods=["GET"])
@jwt_required()
def get_bet_summary():
    user_id = get_jwt_identity().get("id")
    results = db.session.query(
        Bet.date_info,
        func.sum(Bet.amount).label('total_amount')
    ).filter(Bet.user_id == user_id).group_by(Bet.date_info).all()

    data = [{"date_info": r[0], "total_amount": float(r[1])} for r in results]
    return jsonify(data)
