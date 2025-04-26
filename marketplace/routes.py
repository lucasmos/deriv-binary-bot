from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import marketplace_bp
from .services import MarketplaceService
from .forms import StrategyUploadForm, ReviewForm
from .pricing import calculate_price

@marketplace_bp.route('/strategy/<int:strategy_id>')
@login_required
def strategy_detail(strategy_id):
    service = MarketplaceService()
    strategy = service.get_strategy_by_id(strategy_id)
    reviews = service.get_strategy_reviews(strategy_id)
    owned = service.has_purchased(current_user.id, strategy_id)
    
    form = ReviewForm()
    return render_template('marketplace/strategy_detail.html', 
                         strategy=strategy,
                         reviews=reviews,
                         owned=owned,
                         form=form)

@marketplace_bp.route('/purchase/<int:strategy_id>', methods=['POST'])
@login_required
def purchase_strategy(strategy_id):
    service = MarketplaceService()
    success, message = service.purchase_strategy(current_user.id, strategy_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('marketplace.strategy_detail', strategy_id=strategy_id))

@marketplace_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_strategy():
    form = StrategyUploadForm()
    
    if form.validate_on_submit():
        service = MarketplaceService()
        success, strategy = service.upload_strategy(
            current_user.id,
            form.name.data,
            form.description.data,
            form.price.data,
            form.category.data,
            form.strategy_file.data
        )
        
        if success:
            flash('Strategy uploaded successfully!', 'success')
            return redirect(url_for('marketplace.strategy_detail', strategy_id=strategy.id))
        else:
            flash('Error uploading strategy', 'danger')
    
    return render_template('marketplace/create_strategy.html', form=form)

@marketplace_bp.route('/my-strategies')
@login_required
def my_strategies():
    service = MarketplaceService()
    purchased = service.get_user_purchases(current_user.id)
    uploaded = service.get_user_uploaded_strategies(current_user.id)
    return render_template('marketplace/my_strategies.html', 
                         purchased=purchased,
                         uploaded=uploaded)