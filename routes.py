from app import db
from models import Login,Admin,Professional,Customer,Service,ServiceRequest
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user,login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


# from plotly import *
import plotly.graph_objs as go
from plotly.subplots import *

routes_bp = Blueprint("routes", __name__)

def register_routes(app,db):
    @routes_bp.route('/')
    @routes_bp.route('/login', methods=['GET', 'POST'])
    def login():
        
        if request.method == 'POST':
            email = request.form.get("email")
            password = request.form.get("password")
            user = Login.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    if user.user_type == 'professional':
                        professional = Professional.query.filter_by(login_id=user.id).first()
                        if professional and professional.is_approved is True:
                            flash("Logged in!", category='success')
                            login_user(user, remember=True)
                            return redirect(url_for('home'))
                        elif professional and professional.is_approved is False:
                            flash('Your account has been rejected by admin.', category='error')
                        else:
                            flash('Your account is waiting for admin approval.', category='error')
                    else:
                        flash("Logged in!", category='success')
                        login_user(user, remember=True)
                        return redirect(url_for('home'))
                    
                    
                else:
                    flash('Password is incorrect.', category='error')
            else:
                flash('Email does not exist.', category='error')

        return render_template("login.html", user=current_user)

    @routes_bp.route('/register/professional', methods=['GET', 'POST'])
    def professional_register():
        services = Service.query.all()
        if request.method == 'POST':
            email = request.form.get("Email")
            password = request.form.get("Password")
            full_name = request.form.get("FullName")
            service_id = request.form.get("ServiceID")
            experience = request.form.get("Experience")
            address = request.form.get("Address")
            pincode = request.form.get("Pincode")
            email_exists = Professional.query.filter_by(email=email).first()
            if email_exists:
                flash('Email is already in use.', category='error')            
            else:
                new_login = Login(
                    user_type='professional',
                    email=email,
                    password=generate_password_hash(password, method='sha256')
                )
                db.session.add(new_login)
                db.session.commit()
                new_professional = Professional(                    
                    full_name=full_name,
                    service_id=service_id,
                    experience=experience,
                    address=address,
                    pincode=pincode,
                    login_id=new_login.id
                )
                db.session.add(new_professional)
                db.session.commit()                
                flash('User created!')
                return redirect(url_for('home'))
        return render_template("professional_register.html",services=services)
    
    @routes_bp.route('/register/customer', methods=['GET', 'POST'])
    def customer_register():        
        if request.method == 'POST':
            email = request.form.get("Email")
            password = request.form.get("Password")
            full_name = request.form.get("FullName")
            address = request.form.get("Address")
            pincode = request.form.get("Pincode")
            email_exists = Customer.query.filter_by(email=email).first()
            if email_exists:
                flash('Email is already in use.', category='error')            
            else:
                new_login = Login(
                    user_type='customer',
                    email=email,
                    password=generate_password_hash(password, method='sha256')
                )
                db.session.add(new_login)
                db.session.commit()
                new_customer = Customer(                    
                    full_name=full_name,                    
                    address=address,
                    pincode=pincode,
                    login_id=new_login.id
                )
                db.session.add(new_customer)
                db.session.commit()
                login_user(new_login, remember=True)
                flash('User created!')
                return redirect(url_for('home'))
        return render_template("customer_register.html")
    
    @routes_bp.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
    
    
    @routes_bp.route('/home')
    @login_required
    def home():
        if current_user.user_type == 'admin':
            return redirect(url_for('admin_home'))
        elif current_user.user_type == 'professional':
            return redirect(url_for('professional_home'))
        elif current_user.user_type == 'customer':
            return redirect(url_for('customer_home'))
        else:
            return redirect(url_for('login'))
    
    @routes_bp.route('/search')
    @login_required
    def search():
        if current_user.user_type == 'admin':
            return redirect(url_for('admin_search'))
        elif current_user.user_type == 'professional':
            return redirect(url_for('professional_search'))
        elif current_user.user_type == 'customer':
            return redirect(url_for('customer_search'))
        else:
            return redirect(url_for('login'))
        
    @routes_bp.route('/summary')
    @login_required
    def summary():
        if current_user.user_type == 'admin':
            return redirect(url_for('admin_summary'))
        elif current_user.user_type == 'professional':
            return redirect(url_for('professional_summary'))
        elif current_user.user_type == 'customer':
            return redirect(url_for('customer_summary'))
        else:
            return redirect(url_for('login'))
    
    
    
        
    # Admin Home Route
    @routes_bp.route('/home/admin')
    @login_required
    def admin_home():
        return render_template(
            "admin_home.html",
            services=Service.query.all(),
            professionals=Professional.query.all(),
            service_requests=ServiceRequest.query.all()
            )
    @routes_bp.route('/admin/services/new')
    @login_required
    def new_service():
        return render_template('services.html')

    @routes_bp.route('/admin/services/edit/<int:service_id>', methods=['POST'])
    @login_required
    def edit_service(service_id):
        service = Service.query.get_or_404(service_id)
        service.service_name = request.form.get('service_name')
        service.description = request.form.get('description')
        service.base_price = request.form.get('base_price')
        service.status = request.form.get('status')
        service.reviews= request.form.get('reviews')
        db.session.commit()
        return redirect(url_for('routes_bp.admin_home'))

    @routes_bp.route('/admin/services/delete/<int:service_id>', methods=['POST'])
    @login_required
    def delete_service(service_id):
        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        return redirect(url_for('routes_bp.admin_home'))

    
    @routes_bp.route('/search/admin', methods=['GET'])
    @login_required
    def admin_search():
        search_type = request.args.get('search_type', 'all')
        search_term = request.args.get('search_term', '')
        results = []    
        if search_term:
            search_term = f"%{search_term}%"       
            if search_type == 'all':
                services = Service.query.filter(Service.service_name.ilike(search_term)).all()
                professionals = Professional.query.filter(Professional.fullname.ilike(search_term)).all()
                service_requests = ServiceRequest.query.join(Professional, ServiceRequest.professional_id == Professional.id).filter(Professional.fullname.ilike(search_term)).all()
                
                results.extend(services)
                results.extend(professionals)
                results.extend(service_requests)
            elif search_type == 'service':
                results = Service.query.filter(Service.service_name.ilike(search_term)).all()
            elif search_type == 'professional':
                results = Professional.query.filter(Professional.fullname.ilike(search_term)).all()
            elif search_type == 'service_request':
                    results = ServiceRequest.query.join(Professional, ServiceRequest.professional_id == Professional.id).filter(Professional.fullname.ilike(search_term)).all()
        return render_template(
            "admin_search.html",
            search_type=search_type,
            search_term=request.args.get('search_term', ''),
            results=results
            )

    # Admin Summary Route
    @routes_bp.route('/summary/admin')
    @login_required
    def admin_summary():
        return render_template("admin_summary.html")

    # Professional Home Route
    @routes_bp.route('/home/professional')
    @login_required
    def professional_home():
        return render_template("professional_home.html")

    # Professional Search Route
    @routes_bp.route('/professional/search')
    @login_required
    def professional_search():
        return render_template("professional_search.html")

    # Professional Summary Route
    @routes_bp.route('/professional/summary')
    @login_required
    def professional_summary():
        return render_template("professional_summary.html")

    # Customer Home Route
    @routes_bp.route('/home/customer')
    @login_required
    def customer_home():
        return render_template("customer_home.html")

    # Customer Search Route
    @routes_bp.route('/customer/search')
    @login_required
    def customer_search():
        return render_template("customer_search.html")

    # Customer Summary Route
    @routes_bp.route('/customer/summary')
    @login_required
    def customer_summary():
        return render_template("customer_summary.html")
            
        
        
        
        
        
        # Fetch data
        total_sponsors = Sponsor.query.count()
        total_influencers = Influencer.query.count()
        total_users = {'sponsors': total_sponsors, 'influencers': total_influencers}

        
        influencer_data = []
        campaigns = Campaign.query.all()
        public_campaigns = len(Campaign.query.filter_by(visibility='public').all())
        private_campaigns = len(Campaign.query.filter_by(visibility='private').all())
        for campaign in campaigns:
            ads = Ad.query.filter_by(campaign_id=campaign.id).all()
            influencers = {}
            for ad in ads:
                influencer = Influencer.query.get(ad.influencer_id)
                if influencer.id not in influencers:
                    influencers[influencer.id] = {
                        'influencer': influencer,
                        'ads': []
                    }
                influencers[influencer.id]['ads'].append(ad)
        
            campaign_influencers = []
            for influencer_id, data in influencers.items():
                campaign_influencers.append(data)
            
            influencer_data.append({
                'campaign': campaign,
                'influencers': campaign_influencers
            })
                
        

        ad_statuses = db.session.query(Ad.status, db.func.count(Ad.id)).group_by(Ad.status).all()
        ad_labels = [status for status, count in ad_statuses]
        ad_values = [count for status, count in ad_statuses]

        
        flagged_sponsors = Sponsor.query.filter_by(flagged=True).count()
        unflagged_sponsors = total_sponsors - flagged_sponsors
        flagged_influencers = Influencer.query.filter_by(flagged=True).count()
        unflagged_influencers = total_influencers - flagged_influencers

        # Generate charts
        users_pie = go.Figure(data=[go.Pie(
            labels=['Sponsors', 'Influencers'],
            values=[total_sponsors, total_influencers],
            marker=dict(colors=['#36A2EB', '#FFCE56']),
            textinfo='label+percent+value'
        )])
        users_pie.update_layout(template="plotly_dark", title='Users')

        campaigns_pie = go.Figure(data=[go.Pie(
            labels=['Public Campaigns', 'Private Campaigns'],
            values=[public_campaigns, private_campaigns],
            marker=dict(colors=['#4BC0C0', '#F7464A']),
            textinfo='label+percent+value'
        )])
        campaigns_pie.update_layout(template="plotly_dark", title='Campaigns')

        ads_pie = go.Figure(data=[go.Pie(
            labels=ad_labels,
            values=ad_values,
            marker=dict(colors=['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#F7464A']),
            textinfo='label+percent+value'
        )])
        ads_pie.update_layout(template="plotly_dark", title='Ads')

        flagged_users_pie = go.Figure(data=[go.Pie(
            labels=['Flagged Sponsors', 'Flagged Influencers'],
            values=[flagged_sponsors, flagged_influencers],
            marker=dict(colors=['#FF6384', '#36A2EB']),
            textinfo='label+percent+value'
        )])
        flagged_users_pie.update_layout(template="plotly_dark", title='Flagged Users')

        flagged_vs_unflagged_sponsors = go.Figure(data=[go.Pie(
            labels=['Flagged Sponsors', 'Unflagged Sponsors'],
            values=[flagged_sponsors, unflagged_sponsors],
            marker=dict(colors=['#FF6384', '#36A2EB']),
            textinfo='label+percent+value'
        )])
        flagged_vs_unflagged_sponsors.update_layout(template="plotly_dark", title='Flagged vs Unflagged Sponsors')

        flagged_vs_unflagged_influencers = go.Figure(data=[go.Pie(
            labels=['Flagged Influencers', 'Unflagged Influencers'],
            values=[flagged_influencers, unflagged_influencers],
            marker=dict(colors=['#FF6384', '#36A2EB']),            
            textinfo='label+percent+value'
        )])
        flagged_vs_unflagged_influencers.update_layout(template="plotly_dark", title='Flagged vs Unflagged Influencers')

        # Save charts as images
        if not os.path.exists(os.path.join(app.root_path, 'static', 'charts')):
            os.makedirs(os.path.join(app.root_path, 'static', 'charts'))

        users_pie.write_image(os.path.join(app.root_path, 'static', 'charts', 'users_pie.png'))
        campaigns_pie.write_image(os.path.join(app.root_path, 'static', 'charts', 'campaigns_pie.png'))
        ads_pie.write_image(os.path.join(app.root_path, 'static', 'charts', 'ads_pie.png'))
        flagged_users_pie.write_image(os.path.join(app.root_path, 'static', 'charts', 'flagged_users_pie.png'))
        flagged_vs_unflagged_sponsors.write_image(os.path.join(app.root_path, 'static', 'charts', 'flagged_vs_unflagged_sponsors.png'))
        flagged_vs_unflagged_influencers.write_image(os.path.join(app.root_path, 'static', 'charts', 'flagged_vs_unflagged_influencers.png'))


        return render_template(
            'admin_home.html',
            total_users=total_users,
            admins=Admin.query.all(),
            sponsors=Sponsor.query.all(),
            influencers=Influencer.query.all(),
            campaigns=campaigns,
            influencer_data = influencer_data,
            public_campaigns=public_campaigns,
            private_campaigns=private_campaigns,
            ads=Ad.query.all(),
            ad_statuses=dict(ad_statuses),
            flagged_sponsors=flagged_sponsors,
            flagged_influencers=flagged_influencers,
            users_chart_path=url_for('static', filename='charts/users_pie.png'),
            campaigns_chart_path=url_for('static', filename='charts/campaigns_pie.png'),
            ads_chart_path=url_for('static', filename='charts/ads_pie.png'),
            flagged_users_chart_path=url_for('static', filename='charts/flagged_users_pie.png'),
            flagged_vs_unflagged_sponsors_chart_path=url_for('static', filename='charts/flagged_vs_unflagged_sponsors.png'),
            flagged_vs_unflagged_influencers_chart_path=url_for('static', filename='charts/flagged_vs_unflagged_influencers.png')    
        )

    @routes_bp.route('/flag_sponsor/<int:sponsor_id>', methods=['POST'])
    def flag_sponsor(sponsor_id):
        sponsor = Sponsor.query.get_or_404(sponsor_id)
        sponsor.flagged = not sponsor.flagged
        db.session.commit()
        return redirect(url_for('admin_home'))

    @routes_bp.route('/flag_influencer/<int:influencer_id>', methods=['POST'])
    def flag_influencer(influencer_id):
        influencer = Influencer.query.get_or_404(influencer_id)
        influencer.flagged = not influencer.flagged
        db.session.commit()
        return redirect(url_for('admin_home'))

    

    @routes_bp.route('/influencer/home', methods=['GET', 'POST'])
    @login_required
    def influencer_home():
        influencer = db.session.query(Influencer).join(Login).filter(Login.id == current_user.id).first_or_404()
        if request.method == 'POST':
            if 'update_profile' in request.form:
                influencer.name = request.form.get('name', influencer.name)
                influencer.category = request.form.get('category', influencer.category)
                influencer.total_followers = request.form.get('total_followers', influencer.total_followers)
                influencer.active_followers = request.form.get('active_followers', influencer.active_followers)
                influencer.niche = request.form.get('niche', influencer.niche)
                db.session.commit()
                flash('Profile updated successfully!')
        search_query = request.form.get('search_query')
        search_filter = request.form.get('search_filter')

        if search_query:
            
            if search_filter == 'budget':
                campaigns_search = Campaign.query.filter(Campaign.budget >= float(search_query)).all()
            elif search_filter == 'goals':
                campaigns_search = Campaign.query.filter(Campaign.goals.ilike(f"%{search_query}%")).all()
        else:
            campaigns_search = ""

        influencer_data = []
        campaigns = Campaign.query.join(Ad).filter(Ad.influencer_id == influencer.id, Campaign.visibility == 'public').all()        
        campaigns_with_ads = []
        for campaign in campaigns:
            ads = Ad.query.filter_by(campaign_id=campaign.id, influencer_id=influencer.id).all()
            for ad in ads:
                ad.sponsor = Sponsor.query.get(ad.sponsor_id)
            campaigns_with_ads.append({
                'campaign': campaign,
                'ads': ads
            })

        influencer_data.append({
            'influencer': influencer,
            'campaigns_with_ads': campaigns_with_ads
        })

        
        edit_mode = request.args.get('edit_mode', 'False') == 'True'
        ad_id = request.args.get('ad_id')

        return render_template(
            'influencer_home.html',
            campaigns_search=campaigns_search,
            influencers=influencer,
            influencer_data=influencer_data,
            edit_mode=edit_mode,
            ad_id=ad_id,
            
        )
    
    @routes_bp.route('/ad_status/<int:ad_id>', methods=['POST'])
    def ad_status(ad_id):
        ad = Ad.query.get_or_404(ad_id)
        ad.status = request.form.get('ad')
        db.session.commit()
        return redirect(url_for('influencer_home'))
    
    @routes_bp.route('/influencer/negotiate/<int:ad_id>', methods=['POST'])
    
    def negotiate(ad_id):
        action = request.form.get('action')
        if action == 'negotiate':
            return redirect(url_for('influencer_home', edit_mode=True, ad_id=ad_id))
        elif action == 'submit':
            ad = Ad.query.get_or_404(ad_id)
            ad.payment_amount = request.form.get('amt')
            ad.status = "Negotiated"
            db.session.commit()
            return redirect(url_for('influencer_home', edit_mode=False))
        return redirect(url_for('influencer_home', edit_mode=False))
    
    @routes_bp.route('/sponsor_home', methods=['GET', 'POST'])
    @login_required
    def sponsor_home():
        sponsor = db.session.query(Sponsor).join(Login).filter(Login.id == current_user.id).first_or_404()
        if request.method == 'POST':
            if 'update_profile' in request.form:
                sponsor.name = request.form.get('name', sponsor.name)
                sponsor.industry = request.form.get('industry', sponsor.industry)
                sponsor.budget = request.form.get('budget', sponsor.budget)
                
                db.session.commit()
                flash('Profile updated successfully!')

        
        search_query = request.form.get('search_query')
        search_filter = request.form.get('search_filter')

        if search_query:
            if search_filter == 'name':
                influencers = Influencer.query.filter(Influencer.name.ilike(f"%{search_query}%")).all()
            elif search_filter == 'category':
                influencers = Influencer.query.filter(Influencer.category.ilike(f"%{search_query}%")).all()
            elif search_filter == 'total_followers':
                influencers = Influencer.query.filter(Influencer.total_followers >= int(search_query)).all()
            elif search_filter == 'active_followers':
                influencers = Influencer.query.filter(Influencer.active_followers >= int(search_query)).all()
        else:
            influencers = ""
        campaigns =Campaign.query.filter(Campaign.sponsor_id == Sponsor.id).all()
        influencer_data=Influencer.query.all()        

        return render_template('sponsor_home.html', influencers=influencers, campaigns=campaigns, sponsor=sponsor, influencer_data=influencer_data)
    
    @routes_bp.route('/create_campaign', methods=['POST'])
    def create_campaign():  
            
        name = request.form.get('name')
        description = request.form.get('description')
        start_date_raw = request.form.get('start_date')
        end_date_raw = request.form.get('end_date')        
        start_date = datetime.strptime(start_date_raw, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_raw, '%Y-%m-%d').date()
        budget = request.form.get('budget')
        visibility = request.form.get('visibility')
        goals = request.form.get('goals')
        sponsor = db.session.query(Sponsor).join(Login).filter(Login.id == current_user.id).first_or_404()
        sponsor_id = sponsor.id
        new_campaign = Campaign(name=name,description=description, start_date=start_date, end_date=end_date, budget=budget, visibility=visibility, goals=goals,sponsor_id=sponsor_id)
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!')
        return redirect(url_for('sponsor_home'))

    @routes_bp.route('/update_campaign/<int:campaign_id>', methods=['POST'])
    def update_campaign(campaign_id):
        campaign = Campaign.query.get(campaign_id)
        campaign.name = request.form['name']
        campaign.description = request.form['description']
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        campaign.budget = request.form['budget']
        db.session.commit()
        flash('Campaign updated successfully!')
        return redirect(url_for('sponsor_home'))

    @routes_bp.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
    def delete_campaign(campaign_id):
        campaign = Campaign.query.get(campaign_id)
        db.session.delete(campaign)
        db.session.commit()
        flash('Campaign deleted successfully!')
        return redirect(url_for('sponsor_home'))

    @routes_bp.route('/create_ad_request/<int:campaign_id>', methods=['POST'])
    def create_ad_request(campaign_id):
        influencer_id = int(request.form.get('influencer_id', ''))
        messages= request.form.get('messages', '')
        requirements = request.form.get('requirements', '')
        payment_amount = request.form.get('payment_amount', '0')
        status = 'Pending'
        campaign = Campaign.query.get_or_404(campaign_id)
        sponsor_id = campaign.sponsor_id
        new_ad = Ad(campaign_id=campaign_id, influencer_id=influencer_id, messages=messages, requirements=requirements, payment_amount=payment_amount, status=status,sponsor_id=sponsor_id)
        db.session.add(new_ad)
        db.session.commit()
        flash('Ad request created successfully!')
        return redirect(url_for('sponsor_home'))

    @routes_bp.route('/update_ad_request/<int:ad_id>', methods=['POST'])
    def update_ad_request(ad_id):
        ad = Ad.query.get(ad_id)
        ad.influencer_id = int(request.form['influencer_id'])
        ad.requirements = request.form['requirements']
        ad.payment_amount = request.form['payment_amount']
        ad.status = 'Pending'
        db.session.commit()
        flash('Ad request updated successfully!')
        return redirect(url_for('sponsor_home'))

    @routes_bp.route('/delete_ad_request/<int:ad_id>', methods=['POST'])
    def delete_ad_request(ad_id):
        ad = Ad.query.get(ad_id)
        db.session.delete(ad)
        db.session.commit()
        flash('Ad request deleted successfully!')
        return redirect(url_for('sponsor_home'))
    