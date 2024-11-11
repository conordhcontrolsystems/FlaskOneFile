from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for, send_file, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user  # handles user login for site
from markupsafe import Markup, escape  # markup marks a string as safe HTML that
# shouldn't be escaped by the template engine
#  escapes special characters in a string to prevent Cross-site Scripting (XSS) attacks
#  by converting them to HTML-safe sequences
from jinja2 import pass_context # pass_context allows a Jinja2 filter to access the current template context
# which can include information whether autoescaping is enabled
import os
from os import path
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from datetime import datetime
from weasyprint import HTML


app = Flask(__name__)  # creates instance of Flask class - initializing web app


app.config['SECRET_KEY'] = 'happy days'  # set secret key
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"  # configures database URI for SQLAlchemy
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)

# Models.py 

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    invoices = db.relationship('Invoice', backref='author', lazy=True, cascade="all, delete-orphan")
    quotes = db.relationship('Quote', backref='author', lazy=True, cascade="all, delete-orphan")
    company_name = db.Column(db.String(150), nullable=False)
    company_address1 = db.Column(db.String(150), nullable=False)
    company_address2 = db.Column(db.String(150), nullable=False)
    company_city = db.Column(db.String(150), nullable=False)
    company_county = db.Column(db.String(150), nullable=False)
    company_postcode = db.Column(db.String(10), nullable=False)
    company_country = db.Column(db.String(250), nullable=False)
    company_tel_number = db.Column(db.String(15), nullable=False)
    company_reg_number = db.Column(db.String(15), nullable=False)
    sort_code = db.Column(db.String(10), nullable=False)
    account_number = db.Column(db.String(15), nullable=False)
    bank = db.Column(db.String(50), nullable=False)
    company_logo = db.Column(db.Text)


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(150), nullable=False)
    client_address1 = db.Column(db.String(250), nullable=False)
    client_address2 = db.Column(db.String(250), nullable=False)
    client_city = db.Column(db.String(150), nullable=False)
    client_county = db.Column(db.String(150), nullable=False)
    client_postcode = db.Column(db.String(250), nullable=False)
    client_country = db.Column(db.String(250), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    date_issued = db.Column(db.Date, nullable=False)
    invoice_number = db.Column(db.String(20), nullable=False)  # You can use Text for detailed info
    invoice_reference = db.Column(db.String(100), nullable=False)
    vat_number = db.Column(db.String(20), nullable=False)
    vat_rate = db.Column(db.Float, nullable=False)
    subtotal_total = db.Column(db.Float, nullable=False)
    vat_total = db.Column(db.Float, nullable=False)
    invoice_total = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Invoice {self.id} - {self.client_name}>'


class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    item_description = db.Column(db.String(255), nullable=False)  # Change from item_descriptions to item_description
    quantity = db.Column(db.Float, nullable=False)  # Change from quantities to quantity
    unit_price = db.Column(db.Float, nullable=False)  # Change from unit_prices to unit_price
    subtotal = db.Column(db.Float, nullable=False)
    vat_total = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)


class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(150), nullable=False)
    client_address1 = db.Column(db.String(250), nullable=False)
    client_address2 = db.Column(db.String(250), nullable=False)
    client_city = db.Column(db.String(150), nullable=False)
    client_county = db.Column(db.String(150), nullable=False)
    client_postcode = db.Column(db.String(250), nullable=False)
    client_country = db.Column(db.String(250), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    date = db.Column(db.Date, nullable=False)
    quote_number = db.Column(db.String(20), nullable=False)  # You can use Text for detailed info
    quote_reference = db.Column(db.String(100), nullable=False)
    quote_notes = db.Column(db.String(500), nullable=False)
    vat_number = db.Column(db.String(20), nullable=False)
    vat_rate = db.Column(db.Float, nullable=False)
    subtotal_total = db.Column(db.Float, nullable=False)
    vat_total = db.Column(db.Float, nullable=False)
    quote_total = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.relationship('QuoteItem', backref='quote', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Quote {self.id} - {self.client_name}>'


class QuoteItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)
    item_description = db.Column(db.String(255), nullable=False)  # Change from item_descriptions to item_description
    quantity = db.Column(db.Float, nullable=False)  # Change from quantities to quantity
    unit_price = db.Column(db.Float, nullable=False)  # Change from unit_prices to unit_price
    subtotal = db.Column(db.Float, nullable=False)
    vat_total = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Add user_id here
    client_name = db.Column(db.String(100))
    client_address1 = db.Column(db.String(100))
    client_address2 = db.Column(db.String(100), nullable=True)
    client_city = db.Column(db.String(100))
    client_county = db.Column(db.String(100))
    client_postcode = db.Column(db.String(20))
    client_country = db.Column(db.String(50))

    # Define the relationship (optional)
    user = db.relationship('User', backref='clients')

    def to_dict(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "client_address1": self.client_address1,
            "client_address2": self.client_address2,
            "client_city": self.client_city,
            "client_county": self.client_county,
            "client_postcode": self.client_postcode,
            "client_country": self.client_country,
        }

with app.app_context():
        db.create_all()  # creates database tables defined by the models


# pdf_generator.py

def generate_invoice_pdf(rendered_html, invoice):
    # Render the invoice template to HTML
    html = rendered_html

    # Define the directory to save PDFs
    pdf_dir = os.path.join(os.getcwd(), 'invoices_pdfs')
    os.makedirs(pdf_dir, exist_ok=True)

    pdf_filename = f'invoice_{invoice.id}.pdf'
    pdf_path = os.path.join(pdf_dir, pdf_filename)

    # Generate PDF and save, specifying base_url for resolving static files
    HTML(string=html, base_url=current_app.root_path).write_pdf(pdf_path)

    return pdf_path


def generate_quote_pdf(rendered_html, quote):
    # Render the invoice template to HTML
    html = rendered_html

    # Define the directory to save PDFs
    pdf_dir = os.path.join(os.getcwd(), 'quote_pdfs')
    os.makedirs(pdf_dir, exist_ok=True)

    pdf_filename = f'quote_{quote.id}.pdf'
    pdf_path = os.path.join(pdf_dir, pdf_filename)

    # Generate PDF and save, specifying base_url for resolving static files
    HTML(string=html, base_url=current_app.root_path).write_pdf(pdf_path)

    return pdf_path

# Auth.py

auth = Blueprint('auth', __name__)  # Easiest to name 'views' same as file name. __name__ is how you define a Blueprint


@auth.route('/login', methods=['GET', 'POST'])  # can now accept both get and post requests
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()  # filter users with this email here
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required  # adding this decorator means you cant access this unless you are already logged in
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])  # can now accept both get and post requests
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')  # This is how you get information from the form sign_up.html
        company_name = request.form.get('companyName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        company_address1 = request.form.get('companyAddress1')
        company_address2 = request.form.get('companyAddress2')
        company_city = request.form.get('companyCity')
        company_county = request.form.get('companyCounty')
        company_postcode = request.form.get('companyPostcode')
        company_country = request.form.get('companyCountry')
        company_tel_number = request.form.get('companyTel')
        company_reg_number = request.form.get('companyReg')
        bank = request.form.get('bank')
        sort_code = request.form.get('sortCode')
        account_number = request.form.get('accountNumber')

        # Handle the logo file upload and convert it to Base64
        company_logo_file = request.files.get('companyLogo')

        if company_logo_file and company_logo_file.filename != '':
            # Read file content as binary
            logo_data = company_logo_file.read()
            # Encode the binary data to Base64
            logo_base64 = base64.b64encode(logo_data).decode('utf-8')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
            return render_template("sign_up.html", user=current_user)  # Add a return here to stop execution

        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(company_name) < 2:
            flash('Company name must be greater than 1 character', category='error')
        elif password1 != password2:
            flash('Passwords dont match', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:  # creating new user
            new_user = User(email=email, company_name=company_name, company_address1=company_address1,
                            company_address2=company_address2, company_city=company_city,
                            company_county=company_county, company_postcode=company_postcode,
                            company_country=company_country, company_logo=logo_base64,
                            company_tel_number=company_tel_number, company_reg_number=company_reg_number,
                            bank=bank, sort_code=sort_code, account_number=account_number,
                            password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            # re-direct to homepage
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


# views.py

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():
    invoices = Invoice.query.filter_by(user_id=current_user.id).order_by(Invoice.date_issued.desc()).all()
    quotes = Quote.query.filter_by(user_id=current_user.id).order_by(Quote.date.desc()).all()
    return render_template("home.html", user=current_user, invoices=invoices, quotes=quotes)


@views.route('/account-details', methods=['GET', 'POST'])
@login_required
def account():
    invoices = Invoice.query.filter_by(user_id=current_user.id).order_by(Invoice.date_issued.desc()).all()
    quotes = Quote.query.filter_by(user_id=current_user.id).order_by(Quote.date.desc()).all()

    if request.method == 'POST':
        # Fetch form data
        email = request.form.get('email') or current_user.email
        company_name = request.form.get('companyName') or current_user.company_name
        company_address1 = request.form.get('companyAddress1') or current_user.company_address1
        company_address2 = request.form.get('companyAddress2') or current_user.company_address2
        company_city = request.form.get('companyCity') or current_user.company_city
        company_county = request.form.get('companyCounty') or current_user.company_county
        company_postcode = request.form.get('companyPostcode') or current_user.company_postcode
        company_country = request.form.get('companyCountry') or current_user.company_country
        company_tel_number = request.form.get('companyTel') or current_user.company_tel_number
        company_reg_number = request.form.get('companyReg') or current_user.company_reg_number
        bank = request.form.get('bank') or current_user.bank
        sort_code = request.form.get('sortCode') or current_user.sort_code
        account_number = request.form.get('accountNumber') or current_user.account_number

        # Handle the logo file upload and convert it to Base64
        company_logo_file = request.files.get('companyLogo')

        if company_logo_file and company_logo_file.filename != '':
            # Read file content as binary
            logo_data = company_logo_file.read()
            # Encode the binary data to Base64
            logo_base64 = base64.b64encode(logo_data).decode('utf-8')
            # Update user's company logo with the Base64 string
            current_user.company_logo = logo_base64

        # Update existing user's details
        current_user.email = email
        current_user.company_name = company_name
        current_user.company_address1 = company_address1
        current_user.company_address2 = company_address2
        current_user.company_city = company_city
        current_user.company_county = company_county
        current_user.company_postcode = company_postcode
        current_user.company_country = company_country
        current_user.company_tel_number = company_tel_number
        current_user.company_reg_number = company_reg_number
        current_user.bank = bank
        current_user.sort_code = sort_code
        current_user.account_number = account_number

        # Commit changes to the database
        db.session.commit()
        flash('Details Updated!', category='success')

        # Redirect to the home page
        return redirect(url_for('views.home'))

    return render_template("account_details.html", user=current_user, invoices=invoices, quotes=quotes)


@views.route('/create-invoice', methods=['GET', 'POST'])
@login_required
def create_invoice():
    if request.method == 'POST':
        # Get the number of items from the form
        num_items = int(request.form.get('numItems'))  # used in JS script in create_invoice.html

        # Fetch client and invoice data
        client_name = request.form.get('clientName')
        client_address1 = request.form.get('clientAddress1')
        client_address2 = request.form.get('clientAddress2')
        client_city = request.form.get('clientCity')
        client_county = request.form.get('clientCounty')
        client_postcode = request.form.get('clientPostcode')
        client_country = request.form.get('clientCountry')
        invoice_number = request.form.get('invoiceNumber')
        invoice_reference = request.form.get('invoiceReference')
        date_issued_str = request.form.get('issueDate')
        vat_number = request.form.get('vatNumber')
        vat_rate = request.form.get('vatRate')
        due_date_str = request.form.get('dueDate')

        # Get whether to save the client information
        save_client = 'saveClient' in request.form

        # If the checkbox is checked, save client info
        if save_client:
            new_client = Client(
                client_name=client_name,
                client_address1=client_address1,
                client_address2=client_address2,
                client_city=client_city,
                client_county=client_county,
                client_postcode=client_postcode,
                client_country=client_country,
                user_id=current_user.id  # Assuming the user is associated with the client
            )
            db.session.add(new_client)  # Add client to session
            db.session.commit()  # Commit to save client information

        # convert string dates to dates
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        date_issued = datetime.strptime(date_issued_str, '%Y-%m-%d').date()

        # Convert VAT rate to float, with a default if invalid
        try:
            vat_rate_float = float(vat_rate)
        except ValueError:
            vat_rate_float = 0.0  # Default to 0.0 if invalid value is provided

        # Initialize total variable for the invoice total
        total_subtotal = 0.0
        total_vat = 0.0
        total_amount = 0.0

        # List to hold created invoice items
        invoice_items = []

        # Loop through each item and retrieve form data
        for i in range(1, num_items + 1):
            item_desc = request.form.get(f'item{i}_description')
            qty = request.form.get(f'item{i}_quantity')
            unit_price = request.form.get(f'item{i}_price')

            try:
                qty = float(qty) if qty else 0.0
                unit_price = float(unit_price) if unit_price else 0.0
            except ValueError:
                qty = 0.0  # Default to 0 if invalid value is provided
                unit_price = 0.0  # Default to 0 if invalid value is provided

            # Only create InvoiceItem if quantity is greater than 0
            if qty > 0 and item_desc:
                # Calculate total for the current item
                item_total = qty * unit_price
                item_vat = item_total * (vat_rate_float / 100)  # Calculate VAT for this item
                item_total_with_vat = item_total + item_vat  # Total including VAT

                # Create a new InvoiceItem object
                invoice_item = InvoiceItem(
                    item_description=item_desc,
                    quantity=qty,
                    unit_price=unit_price,
                    subtotal=item_total,
                    vat_total=item_vat,  # VAT for the item
                    total=item_total_with_vat,  # Total including VAT
                )

                # Accumulate the total for the invoice
                total_subtotal += item_total
                total_vat += item_vat
                total_amount += item_total_with_vat

                # Add the item to the list for later insertion
                invoice_items.append(invoice_item)

        # Create new invoice object
        new_invoice = Invoice(
            due_date=due_date,
            date_issued=date_issued,
            client_name=client_name,
            client_address1=client_address1,
            client_address2=client_address2,
            client_city=client_city,
            client_county=client_county,
            client_postcode=client_postcode,
            client_country=client_country,
            invoice_number=invoice_number,
            invoice_reference=invoice_reference,
            vat_number=vat_number,
            vat_rate=vat_rate_float,  # Include VAT rate here
            subtotal_total=total_subtotal,
            vat_total=total_vat,
            invoice_total=total_amount,  # Set the calculated invoice total
            author=current_user
        )

        # Add the new invoice to the database and commit to get the ID
        db.session.add(new_invoice)
        db.session.commit()  # This will generate an ID for the new_invoice

        # Set the invoice_id for each InvoiceItem
        for item in invoice_items:
            item.invoice_id = new_invoice.id  # Set the invoice ID

            # Now add the item to the session
            db.session.add(item)

        # Commit the invoice items to the database
        db.session.commit()

        flash('Invoice created successfully!', category='success')
        return redirect(url_for('views.view_invoice', invoice_id=new_invoice.id))

    # Ensure saved_clients and clients_data are defined properly
    saved_clients = Client.query.filter_by(user_id=current_user.id).all()
    clients_data = [{'id': client.id, 'client_name': client.client_name, 'client_address1': client.client_address1,
                         'client_address2': client.client_address2, 'client_city': client.client_city,
                         'client_county': client.client_county, 'client_postcode': client.client_postcode,
                         'client_country': client.client_country} for client in saved_clients]

    return render_template("create_invoice.html", user=current_user, saved_clients=saved_clients,
                               clients_data=clients_data)


@views.route('/invoice/<int:invoice_id>', methods=['GET'])
@login_required
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    user = current_user

    # Ensure the current user owns the invoice
    if invoice.author != current_user:
        flash('You do not have permission to view this invoice.', category='error')
        return redirect(url_for('views.home'))

    # Fetch invoice items related to this invoice
    invoice_items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()

    # Check if company logo exists
    image_base64 = None
    if user.company_logo:
        logo_path = user.company_logo
        if os.path.exists(logo_path):
            # Read and encode the image to base64
            with open(logo_path, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    # Pass the base64 image string and invoice items to the template
    return render_template("view_invoice.html", user=current_user, invoice=invoice, invoice_items=invoice_items,
                           image_base64=image_base64)


@views.route('/invoice/<int:invoice_id>/download', methods=['GET'])
@login_required
def download_invoice(invoice_id):
    # Fetch the invoice object from the database
    invoice = Invoice.query.get_or_404(invoice_id)

    user = current_user

    # Ensure the current user owns the invoice
    if invoice.author != current_user:
        flash('You do not have permission to download this invoice.', category='error')
        return redirect(url_for('views.home'))

    # Fetch invoice items related to this invoice
    invoice_items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()

    # Check if company logo exists
    image_base64 = None
    if user.company_logo:
        logo_path = user.company_logo
        if os.path.exists(logo_path):
            # Read and encode the image to base64
            with open(logo_path, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    # Render the invoice template for the PDF
    rendered_html = render_template('invoice_template.html', invoice=invoice, image_base64=image_base64,
                                    invoice_items=invoice_items, user=current_user)

    # Generate PDF from the rendered HTML
    pdf_path = generate_invoice_pdf(rendered_html, invoice)  # Pass the invoice object here

    # Send the PDF file to the user as a download
    return send_file(pdf_path, as_attachment=True)


@views.route('/delete-invoice/<int:invoice_id>', methods=['POST'])
@login_required
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)

    if invoice.author != current_user:
        flash('You do not have permission to delete this invoice.', category='error')
        return redirect(url_for('views.home'))

    db.session.delete(invoice)
    db.session.commit()
    flash('Invoice deleted successfully!', category='success')
    return redirect(url_for('views.home'))


@views.route('/create-quote', methods=['GET', 'POST'])
@login_required
def create_quote():
    if request.method == 'POST':
        # Get the number of items from the form
        num_items = int(request.form.get('numItems'))  # used in JS script in create_quote.html

        # Fetch client and quote data
        client_name = request.form.get('clientName')
        client_address1 = request.form.get('clientAddress1')
        client_address2 = request.form.get('clientAddress2')
        client_city = request.form.get('clientCity')
        client_county = request.form.get('clientCounty')
        client_postcode = request.form.get('clientPostcode')
        client_country = request.form.get('clientCountry')
        quote_number = request.form.get('quoteNumber')
        quote_reference = request.form.get('quoteReference')
        date_str = request.form.get('date')
        vat_number = request.form.get('vatNumber')
        vat_rate = request.form.get('vatRate')
        expiry_date_str = request.form.get('expiryDate')
        quote_notes = request.form.get('quoteNotes')

        # Get whether to save the client information
        save_client = 'saveClient' in request.form

        # If the checkbox is checked, save client info
        if save_client:
            new_client = Client(
                client_name=client_name,
                client_address1=client_address1,
                client_address2=client_address2,
                client_city=client_city,
                client_county=client_county,
                client_postcode=client_postcode,
                client_country=client_country,
                user_id=current_user.id  # Assuming the user is associated with the client
            )
            db.session.add(new_client)  # Add client to session
            db.session.commit()  # Commit to save client information

        # Convert string dates to dates
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()

        # Convert VAT rate to float, with a default if invalid
        try:
            vat_rate_float = float(vat_rate)
        except ValueError:
            vat_rate_float = 0.0  # Default to 0.0 if invalid value is provided

        # Initialize total variable for the quote total
        total_subtotal = 0.0
        total_vat = 0.0
        total_amount = 0.0

        # List to hold created quote items
        quote_items = []

        # Loop through each item and retrieve form data
        for i in range(1, num_items + 1):
            item_desc = request.form.get(f'item{i}_description')
            qty = request.form.get(f'item{i}_quantity')
            unit_price = request.form.get(f'item{i}_price')

            try:
                qty = float(qty) if qty else 0.0
                unit_price = float(unit_price) if unit_price else 0.0
            except ValueError:
                qty = 0.0  # Default to 0 if invalid value is provided
                unit_price = 0.0  # Default to 0 if invalid value is provided

            # Only create QuoteItem if quantity is greater than 0
            if qty > 0 and item_desc:
                # Calculate total for the current item
                item_total = qty * unit_price
                item_vat = item_total * (vat_rate_float / 100)  # Calculate VAT for this item
                item_total_with_vat = item_total + item_vat  # Total including VAT

                # Create a new QuoteItem object
                quote_item = QuoteItem(
                    item_description=item_desc,
                    quantity=qty,
                    unit_price=unit_price,
                    subtotal=item_total,
                    vat_total=item_vat,  # VAT for the item
                    total=item_total_with_vat,  # Total including VAT
                )

                # Accumulate the total for the quote
                total_subtotal += item_total
                total_vat += item_vat
                total_amount += item_total_with_vat

                # Add the item to the list for later insertion
                quote_items.append(quote_item)

        # Create new quote object
        new_quote = Quote(
            date=date,
            expiry_date=expiry_date,
            client_name=client_name,
            client_address1=client_address1,
            client_address2=client_address2,
            client_city=client_city,
            client_county=client_county,
            client_postcode=client_postcode,
            client_country=client_country,
            quote_number=quote_number,
            quote_reference=quote_reference,
            quote_notes=quote_notes,
            vat_number=vat_number,
            vat_rate=vat_rate_float,  # Include VAT rate here
            subtotal_total=total_subtotal,
            vat_total=total_vat,
            quote_total=total_amount,  # Set the calculated quote total
            author=current_user
        )

        # Add the new quote to the database and commit to get the ID
        db.session.add(new_quote)
        db.session.commit()  # This will generate an ID for the new_invoice

        # Set the quote_id for each InvoiceItem
        for item in quote_items:
            item.quote_id = new_quote.id  # Set the quote ID

            # Now add the item to the session
            db.session.add(item)

        # Commit the quote items to the database
        db.session.commit()

        flash('Quote created successfully!', category='success')
        return redirect(url_for('views.view_quote', quote_id=new_quote.id))

    # Ensure saved_clients and clients_data are defined properly
    saved_clients = Client.query.filter_by(user_id=current_user.id).all()
    clients_data = [{'id': client.id, 'client_name': client.client_name, 'client_address1': client.client_address1,
                     'client_address2': client.client_address2, 'client_city': client.client_city,
                     'client_county': client.client_county, 'client_postcode': client.client_postcode,
                     'client_country': client.client_country} for client in saved_clients]

    return render_template("create_quote.html", user=current_user, saved_clients=saved_clients, clients_data=clients_data)


@views.route('/quote/<int:quote_id>', methods=['GET'])
@login_required
def view_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    user = current_user

    # Ensure the current user owns the quote
    if quote.author != current_user:
        flash('You do not have permission to view this quote.', category='error')
        return redirect(url_for('views.home'))

    # Fetch quote items related to this invoice
    quote_items = QuoteItem.query.filter_by(quote_id=quote.id).all()

    # Check if company logo exists
    image_base64 = None
    if user.company_logo:
        logo_path = user.company_logo
        if os.path.exists(logo_path):
            # Read and encode the image to base64
            with open(logo_path, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    # Pass the base64 image string and quote items to the template
    return render_template("view_quote.html", user=current_user, quote=quote, quote_items=quote_items,
                           image_base64=image_base64)


@views.route('/quote/<int:quote_id>/download', methods=['GET'])
@login_required
def download_quote(quote_id):
    # Fetch the quote object from the database
    quote = Quote.query.get_or_404(quote_id)

    user = current_user

    # Ensure the current user owns the invoice
    if quote.author != current_user:
        flash('You do not have permission to download this quote.', category='error')
        return redirect(url_for('views.home'))

    # Fetch invoice items related to this invoice
    quote_items = QuoteItem.query.filter_by(quote_id=quote.id).all()

    # Check if company logo exists
    image_base64 = None
    if user.company_logo:
        logo_path = user.company_logo
        if os.path.exists(logo_path):
            # Read and encode the image to base64
            with open(logo_path, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    # Render the quote template for the PDF
    rendered_html = render_template('quote_template.html', quote=quote, image_base64=image_base64,
                                    quote_items=quote_items, user=current_user)

    # Generate PDF from the rendered HTML
    pdf_path = generate_quote_pdf(rendered_html, quote)  # Pass the quote object here

    # Send the PDF file to the user as a download
    return send_file(pdf_path, as_attachment=True)


@views.route('/delete-quote/<int:quote_id>', methods=['POST'])
@login_required
def delete_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)

    if quote.author != current_user:
        flash('You do not have permission to delete this quote.', category='error')
        return redirect(url_for('views.home'))

    db.session.delete(quote)
    db.session.commit()
    flash('Quote deleted successfully!', category='success')
    return redirect(url_for('views.home'))


app.register_blueprint(views, url_prefix='/')  # registers blueprints in flask application
app.register_blueprint(auth, url_prefix='/')


login_manager = LoginManager()  # create instance of the LoginManager class
login_manager.login_view = 'auth.login'  # sets endpoint for the login view
login_manager.init_app(app)  # binds login manager to the flask app

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))  # defines how to load a user from the user ID stored in the session

@app.template_filter('nl2br')  # Registers the function as a Jinja2 template filter called nl2br
@pass_context
def nl2br(context, value):
    """Convert newlines to <br> in Jinja2 templates."""
    # Escape the value to prevent XSS
    escaped_value = escape(value)
    # Replace newlines with <br>
    html_value = escaped_value.replace('\n', '<br>')
    return Markup(html_value)  # function converts special characters to HTML-safe equivalents
    # and marks resulting string as safe



if __name__ == '__main__':  # This ensures that the website is only run if this code is run
    app.run(debug=True)  # anytime we change our python code it will re-run the website