"""
Analytics API endpoints.
Provides data for dashboard visualizations and historical trends.
"""

from flask import jsonify, request, Blueprint
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

analytics_bp = Blueprint('analytics', __name__)
from .. import db
from ..models.prediction import PredictionHistory
from .auth import require_auth

logger = logging.getLogger(__name__)

@analytics_bp.route('/summary', methods=['GET'])
@require_auth
def get_summary_stats(current_user):
    """
    Get summary statistics for the dashboard.
    Supports optional `crop` query parameter to filter by a specific crop.
    """
    try:
        crop_filter = request.args.get('crop')
        
        base_query = PredictionHistory.query.filter_by(user_id=current_user.id)
        if crop_filter:
            base_query = base_query.filter(PredictionHistory.recommended_crop == crop_filter)
            
        total_predictions = base_query.count()
        
        if total_predictions == 0:
            return jsonify({
                "status": "success",
                "data": {
                    "total_predictions": 0,
                    "avg_confidence": 0,
                    "top_crop": "N/A",
                    "avg_yield": 0,
                    "avg_actual": 0,
                    "yield_diff": 0,
                    "recent_activity": 0
                }
            }), 200

        # Calculations respecting the crop filter
        avg_confidence = db.session.query(func.avg(PredictionHistory.confidence))\
            .filter(PredictionHistory.user_id == current_user.id)
        if crop_filter:
            avg_confidence = avg_confidence.filter(PredictionHistory.recommended_crop == crop_filter)
        avg_confidence = avg_confidence.scalar() or 0
        
        # Average of predicted yield (only from records that have a prediction)
        avg_yield = db.session.query(
            func.avg(PredictionHistory.predicted_yield)
        ).filter(PredictionHistory.predicted_yield.isnot(None), PredictionHistory.user_id == current_user.id)
        if crop_filter:
            avg_yield = avg_yield.filter(PredictionHistory.recommended_crop == crop_filter)
        avg_yield = avg_yield.scalar() or 0
        
        # Average of ACTUAL yield (only from records where farmer has logged harvest)
        avg_actual = db.session.query(
            func.avg(PredictionHistory.actual_yield)
        ).filter(PredictionHistory.actual_yield.isnot(None), PredictionHistory.user_id == current_user.id)
        if crop_filter:
            avg_actual = avg_actual.filter(PredictionHistory.recommended_crop == crop_filter)
        avg_actual = avg_actual.scalar() or 0
        
        # Yield difference (Difference)
        yield_diff = avg_actual - avg_yield if avg_actual > 0 else 0
        
        # Get most common crop
        top_crop_query = db.session.query(
            PredictionHistory.recommended_crop, 
            func.count(PredictionHistory.recommended_crop).label('count')
        ).filter(PredictionHistory.user_id == current_user.id)\
         .group_by(PredictionHistory.recommended_crop)\
         .order_by(func.count(PredictionHistory.recommended_crop).desc())\
         .first()
        
        top_crop = top_crop_query[0] if top_crop_query else "N/A"
        
        # Recent activity (last 24 hours) - we can keep this or drop it
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_activity = base_query.filter(PredictionHistory.timestamp >= last_24h).count()

        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "data": {
                "total_predictions": total_predictions,
                "avg_confidence": round(float(avg_confidence), 4),
                "top_crop": top_crop,
                "avg_yield": round(float(avg_yield), 2),
                "avg_actual": round(float(avg_actual), 2),
                "yield_diff": round(float(yield_diff), 2),
                "recent_activity": recent_activity
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching summary stats: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve summary statistics"
        }), 500


@analytics_bp.route('/yield-history', methods=['GET'])
@require_auth
def get_yield_history(current_user):
    """
    Get historical average yield grouped by month.
    Accepts optional `days` query parameter (default 365 = 12 months).
    Used for the trend (AreaChart) on the dashboard.
    """
    try:
        days = request.args.get('days', 365, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query average yield grouped by month (SQLite strftime)
        history = db.session.query(
            func.strftime('%Y-%m', PredictionHistory.timestamp).label('month'),
            func.avg(PredictionHistory.predicted_yield).label('avg_yield'),
            func.count(PredictionHistory.id).label('count')
        ).filter(
            PredictionHistory.timestamp >= start_date,
            PredictionHistory.predicted_yield.isnot(None),
            PredictionHistory.user_id == current_user.id
        ).group_by(func.strftime('%Y-%m', PredictionHistory.timestamp))\
         .order_by(func.strftime('%Y-%m', PredictionHistory.timestamp))\
         .all()
        
        # Format to friendly month labels (e.g., "Jan", "Feb")
        formatted_history = []
        for row in history:
            try:
                dt = datetime.strptime(row.month, '%Y-%m')
                label = dt.strftime('%b')  # e.g. "Jan"
            except Exception:
                label = row.month
            formatted_history.append({
                "month": label,
                "yield": round(float(row.avg_yield), 2),
                "count": row.count
            })

        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "data": {
                "history": formatted_history,
                "period_days": days
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching yield history: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve historical data"
        }), 500


@analytics_bp.route('/crop-comparison', methods=['GET'])
@require_auth
def get_crop_comparison(current_user):
    """
    Get average yield per crop type.
    Used for the bar/comparison chart on the dashboard.
    """
    try:
        distribution = db.session.query(
            PredictionHistory.recommended_crop,
            func.count(PredictionHistory.id).label('count'),
            func.avg(PredictionHistory.confidence).label('avg_confidence'),
            func.avg(PredictionHistory.predicted_yield).label('avg_yield')
        ).filter(PredictionHistory.user_id == current_user.id)\
         .group_by(PredictionHistory.recommended_crop)\
         .order_by(func.avg(PredictionHistory.predicted_yield).desc())\
         .all()
        
        formatted_distribution = []
        for row in distribution:
            entry = {
                "crop": row.recommended_crop,
                "count": row.count,
                "avg_confidence": round(float(row.avg_confidence), 4),
            }
            if row.avg_yield is not None:
                entry["yield"] = round(float(row.avg_yield), 2)
            else:
                entry["yield"] = 0
            formatted_distribution.append(entry)

        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "data": {
                "distribution": formatted_distribution
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching crop comparison: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve crop comparison data"
        }), 500

from ..schemas.prediction_schema import PredictionHistoryDumpSchema

@analytics_bp.route('/history-records', methods=['GET'])
@require_auth
def get_history_records(current_user):
    """
    Get all explicit prediction logs saved by the current user.
    """
    try:
        records = PredictionHistory.query.filter_by(user_id=current_user.id)\
            .order_by(PredictionHistory.timestamp.desc()).all()
            
        schema = PredictionHistoryDumpSchema(many=True)
        dumped_records = schema.dump(records)
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "data": dumped_records
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching history records: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve history records"
        }), 500
