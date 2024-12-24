from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user,login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import os
from datetime import datetime
from .models import Login,Admin,Professional,Customer,Service,ServiceRequest
from . import db


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
        # Chart directory
        chart_dir = os.path.join(app.static_folder, 'charts')

        if not os.path.exists(chart_dir):
            os.makedirs(chart_dir)

        # 1. Service Request Chart
        service_requests = ServiceRequest.query.all()
        status_counts = {}
        for req in service_requests:
            status = req.service_status
            status_counts[status] = status_counts.get(status, 0) + 1

        # Update 'pending' to 'requested' for display purposes
        if 'requested' in status_counts:
            statuses = list(status_counts.keys())
            counts = list(status_counts.values())
        else:
            statuses = list(status_counts.keys())
            counts = list(status_counts.values())


        plt.figure(figsize=(8, 6))
        plt.bar(statuses, counts, color=['skyblue', 'lightgreen', 'salmon'])
        plt.title('Service Requests by Status')
        plt.xlabel('Service Status')
        plt.ylabel('Number of Requests')
        plt.savefig(os.path.join(chart_dir, 'service_requests.png'))
        plt.close()


        # 2. Professional Ratings Chart
        professionals = Professional.query.all()
        low_count = 0
        medium_count = 0
        high_count = 0

        for professional in professionals:
            if professional.ratings:
                if professional.ratings < 3:
                    low_count += 1
                elif 3 <= professional.ratings <= 4:
                    medium_count += 1
                else:
                    high_count += 1

        labels = ['Low (<3)', 'Medium (3-4)', 'High (>4)']
        sizes = [low_count, medium_count, high_count]
        colors = ['lightcoral', 'lightskyblue', 'lightgreen']
        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title("Professional Ratings Distribution")
        plt.axis('equal')
        plt.savefig(os.path.join(chart_dir, 'professional_ratings.png'))
        plt.close()
    
        return render_template(
            "admin_summary.html",
            service_request_chart='charts/service_requests.png',
            professional_ratings_chart='charts/professional_ratings.png'
        )
    
    # Professional Home Route
    @routes_bp.route('/home/professional')
    @login_required
    def professional_home():
        professional_id= Professional.query.filter_by(login_id = current_user.id).first().id
        professional = Professional.query.get_or_404(professional_id)
        open_requests = ServiceRequest.query.filter_by(professional_id=professional_id, service_status='requested').all()
        closed_requests = ServiceRequest.query.filter(ServiceRequest.professional_id==professional_id, ServiceRequest.service_status.in_(['assigned', 'closed'])).all()

        return render_template(
            "professional_home.html",
            open_requests = open_requests,
            closed_requests = closed_requests,
            professional = professional
        )
    
    @routes_bp.route('/professional/edit/<int:professional_id>', methods=['POST'])
    @login_required
    def edit_professional(professional_id):
        professional = Professional.query.get_or_404(professional_id)
        professional.fullname = request.form.get('full_name')
        professional.experience = request.form.get('experience')
        professional.address= request.form.get('address')
        professional.pincode = request.form.get('pincode')
        professional.ratings = request.form.get('ratings')
        professional.remarks = request.form.get('remarks')
        db.session.commit()
        return redirect(url_for('routes_bp.professional_home'))


    @routes_bp.route('/professional/service_request/accept/<int:request_id>', methods=['POST'])
    @login_required
    def accept_service_request(request_id):
        service_request = ServiceRequest.query.get_or_404(request_id)
        service_request.service_status = 'assigned'
        db.session.commit()
        return redirect(url_for('routes_bp.professional_home'))


    @routes_bp.route('/professional/service_request/reject/<int:request_id>', methods=['POST'])
    @login_required
    def reject_service_request(request_id):
        service_request = ServiceRequest.query.get_or_404(request_id)
        service_request.service_status = 'closed'
        db.session.commit()
        return redirect(url_for('routes_bp.professional_home'))


    @routes_bp.route('/search/professional')
    @login_required
    def professional_search():
        search_term = request.args.get('search_term', '')
        results = []
        if search_term:
            search_term = f"%{search_term}%"
            professional_id= Professional.query.filter_by(login_id = current_user.id).first().id
            results= ServiceRequest.query.filter(ServiceRequest.professional_id == professional_id, ServiceRequest.service_status.ilike(search_term)).all()
        return render_template(
        "professional_search.html",
        search_term=search_term,
        results=results
        )


    # Professional Summary Route
    @routes_bp.route('/summary/professional')
    @login_required
    def professional_summary():
        # Chart directory
        chart_dir = os.path.join(app.static_folder, 'charts')
        if not os.path.exists(chart_dir):
            os.makedirs(chart_dir)
        # Get current professional id
        professional_id= Professional.query.filter_by(login_id = current_user.id).first().id

        # 1. Service Request Chart
        service_requests = ServiceRequest.query.filter_by(professional_id=professional_id).all()
        status_counts = {}
        for req in service_requests:
            status = req.service_status
            status_counts[status] = status_counts.get(status, 0) + 1
        # Update 'pending' to 'requested' for display purposes
        if 'requested' in status_counts:
            statuses = list(status_counts.keys())
            counts = list(status_counts.values())
        else:
            statuses = list(status_counts.keys())
            counts = list(status_counts.values())
    
        plt.figure(figsize=(8, 6))
        plt.bar(statuses, counts, color=['skyblue', 'lightgreen', 'salmon'])
        plt.title('Service Requests by Status')
        plt.xlabel('Service Status')
        plt.ylabel('Number of Requests')
        plt.savefig(os.path.join(chart_dir, 'professional_service_requests.png'))
        plt.close()


        # 2. Professional Ratings Chart
        professional = Professional.query.filter_by(login_id = current_user.id).first()
        low_count = 0
        medium_count = 0
        high_count = 0
        if professional.ratings:
            if professional.ratings < 3:
                low_count += 1
            elif 3 <= professional.ratings <= 4:
                medium_count += 1
            else:
                high_count += 1

        labels = ['Low (<3)', 'Medium (3-4)', 'High (>4)']
        sizes = [low_count, medium_count, high_count]
        colors = ['lightcoral', 'lightskyblue', 'lightgreen']
        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title("Professional Ratings Distribution")
        plt.axis('equal')
        plt.savefig(os.path.join(chart_dir, 'professional_professional_ratings.png'))
        plt.close()

        return render_template(
            "professional_summary.html",
            service_request_chart='charts/professional_service_requests.png',
            professional_ratings_chart='charts/professional_professional_ratings.png'
        )

    # Customer Home Route
    @routes_bp.route('/home/customer')
    @login_required
    def customer_home():
        customer_id = Customer.query.filter_by(login_id = current_user.id).first().id
        services = Service.query.all()
        customer = Customer.query.get_or_404(customer_id)
        service_requests = ServiceRequest.query.filter_by(customer_id = customer_id).all()

        return render_template(
            "customer_home.html",
            services = services,
            service_requests= service_requests,
            customer = customer
        )


    @routes_bp.route('/customer/book/<int:service_id>/<int:professional_id>', methods=['POST'])
    @login_required
    def book_service_request(service_id,professional_id):
        customer_id = Customer.query.filter_by(login_id=current_user.id).first().id

        new_service_request = ServiceRequest(
        service_id = service_id,
        customer_id = customer_id,
        professional_id = professional_id,
        date_of_request = datetime.now(),
        service_status='requested'
        )
        db.session.add(new_service_request)
        db.session.commit()

        return redirect(url_for('routes_bp.customer_home'))

    @routes_bp.route('/customer/close/<int:request_id>', methods=['POST'])
    @login_required
    def customer_close_request(request_id):
        service_request = ServiceRequest.query.get_or_404(request_id)
        service_request.service_status = 'closed'
        db.session.commit()
        return redirect(url_for('routes_bp.customer_home'))


    @routes_bp.route('/search/customer')
    @login_required
    def customer_search():
        search_term = request.args.get('search_term', '')
        services = Service.query.all()
        results = []
        if search_term:
            search_term = f"%{search_term}%"
            results = Service.query.filter(Service.service_name.ilike(search_term)).all()
        return render_template(
            "customer_search.html",
            search_term= search_term,
            services = services,
            results=results
        )

    # Customer Summary Route
    @routes_bp.route('/summary/customer')
    @login_required
    def customer_summary():
        # Chart directory
        chart_dir = os.path.join(app.static_folder, 'charts')
        if not os.path.exists(chart_dir):
            os.makedirs(chart_dir)
        customer_id= Customer.query.filter_by(login_id=current_user.id).first().id
        # 1. Service Request Chart
        service_requests = ServiceRequest.query.filter_by(customer_id=customer_id).all()
        status_counts = {}
        for req in service_requests:
            status = req.service_status
            status_counts[status] = status_counts.get(status, 0) + 1
        if 'requested' in status_counts:
            statuses = list(status_counts.keys())
            counts = list(status_counts.values())
        else:
            statuses = list(status_counts.keys())
            counts = list(status_counts.values())
        plt.figure(figsize=(8, 6))
        plt.bar(statuses, counts, color=['skyblue', 'lightgreen', 'salmon'])
        plt.title('Service Requests by Status')
        plt.xlabel('Service Status')
        plt.ylabel('Number of Requests')
        plt.savefig(os.path.join(chart_dir, 'customer_service_requests.png'))
        plt.close()
        
        return render_template(
            "customer_summary.html",
            service_request_chart='charts/customer_service_requests.png',
        )
    
    @routes_bp.route('/customer/edit/<int:customer_id>', methods=['POST'])
    @login_required
    def edit_customer(customer_id):
        customer = Customer.query.get_or_404(customer_id)
        customer.fullname = request.form.get('full_name')
        customer.address = request.form.get('address')
        customer.pincode = request.form.get('pincode')
        db.session.commit()
        return redirect(url_for('routes_bp.customer_home'))