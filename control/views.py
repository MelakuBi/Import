from flask import render_template, request, redirect, url_for, Blueprint, flash
from control.models import Declared, Imported, Balance, db
from flask import make_response
from reportlab.lib.pagesizes import letter
from sqlalchemy import or_
from reportlab.pdfgen import canvas
from io import BytesIO
from urllib.parse import quote, unquote
 
 
views = Blueprint('main', __name__)
 
def calc_balance():
    current_balance = Balance.amount - Imported.amount
    return current_balance


#@views.route('/')
#def index():
#    return render_template('/index.html')

@views.route('/')
def home():
    return render_template('index.html')  # Ensure you have this template created

@views.route('/register', methods=['GET', 'POST'])
def register_declared():
    if request.method == 'POST':
        declaration_number = request.form.get('declaration_number')
        date = request.form.getlist('date[]')
        item_names = request.form.getlist('item_name[]')
        amount = request.form.getlist('amount[]')
        amount_units = request.form.getlist('amount_unit[]')
        measurement = request.form.getlist('measurement[]')
        measurement_units = request.form.getlist('measurement_unit[]')

      #Check if the declaration_number already exists

        existing_declared = Declared.query.filter_by(declaration_number=declaration_number).first()

        if existing_declared:
        # Declaration number already exists, show an error message
            flash(f'Declaration number {declaration_number} already exists.', 'error')
            return redirect(url_for('main.register_declared'))

        
        for i in range(len(item_names)):
            dec = Declared(
                declaration_number=declaration_number,
                measurement=measurement[i],
                measurement_unit =measurement_units[i],
                item_name=item_names[i],
                amount=amount[i],
                amount_unit = amount_units[i],
                date= date
            )
            bal = Balance(
                declaration_number=declaration_number,
                item_name=item_names[i],
                amount=amount[i]
            )
            

            db.session.add(dec)
            db.session.commit()
            db.session.close()         
        

            db.session.add(bal)
            db.session.commit()
            db.session.close()

        return redirect(url_for('main.register_declared'))
    

    return redirect(url_for('main.display_declarations'))

    #return render_template('declared.html', declarations=declarations)



@views.route('/display_declarations')
def display_declarations():
    # Get the search term from the query parameters
    search_term = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of rows per page

    # Filter declarations based on the search term
    if search_term:
        declarations = Declared.query.filter(Declared.declaration_number.like(f'%{search_term}%')).paginate(page=page, per_page=per_page)
    else:
        declarations = Declared.query.paginate(page=page, per_page=per_page)

    return render_template('declared.html', declarations=declarations, search_term=search_term)

@views.route('/imported', methods=['GET', 'POST'])
def search_registered():
    if request.method == 'POST':
        # Get form data (search for declaration number)
        declaration_number = request.form.get('declaration_number')

        # Step 1: Check if the declaration_number exists
        existing_declared = Declared.query.filter_by(declaration_number=declaration_number).all()

        if existing_declared:
            # Step 2: Get all items under the declaration number
            declared_items = Balance.query.filter_by(declaration_number=declaration_number).all()

            if declared_items:
                # Render template with the declared items
                return render_template('imported.html', items=declared_items, declaration_number=existing_declared)
            else:
                flash(f'No items found for declaration {declaration_number}.', 'error')
        else:
            flash(f'Declaration number {declaration_number} is not found.', 'error')
    
    # Pagination for already imported items
    already_imported = None
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of rows per page
    already_imported = Imported.query.paginate(page=page, per_page=per_page)

    return render_template('imported.html', imported=already_imported)

@views.route('/register_imported_item', methods=['GET', 'POST'])
def register_imported_item():
    declaration_number = request.args.get('declaration_number')
    item_name = request.args.get('item_name')
    
    if not declaration_number or not item_name:
        flash('Missing declaration number or item name', 'error')
        return redirect(url_for('main.register_imported'))
    decoded_number = unquote(declaration_number)
    declared_item = Declared.query.filter_by(declaration_number=decoded_number, item_name=item_name).first()
    if declared_item:
            if request.method == 'POST':
                # Handle form submission logic (e.g., registering imported items)
                amount = int(request.form.get('amount'))  # Ensure the amount is an integer
                amount_units = request.form.get('amount_unit')
                measurement = request.form.get('measurement')
                measurement_units = request.form.get('measurement_unit')
                date = request.form.get('date')

                # Check if the balance for the item is available
                check_balance = Balance.query.filter_by(declaration_number=declaration_number, item_name=item_name).first()

                if check_balance:
                    if amount <= check_balance.amount:
                        # Step 4: Register the imported item
                        imported_item = Imported(
                            declaration_number=declaration_number,
                            item_name=item_name,
                            amount=amount,
                            amount_unit=amount_units,
                            measurement=measurement,
                            measurement_unit=measurement_units,
                            date=date
                        )

                    # Update the balance
                        check_balance.amount -= amount

                        # Commit the changes
                        db.session.add(imported_item)
                        db.session.add(check_balance)
                        db.session.commit()

                        flash(f'Item {item_name} under declaration {declaration_number} successfully registered as imported.', 'success')
                        return redirect(url_for('main.register_imported_item', declaration_number=declaration_number, item_name=item_name))
                    else:
                        flash(f'Insufficient balance for {item_name} under declaration {decoded_number}.', 'error')

            # Render the template and pass variables to it
            return render_template('register_imported_items.html', item=declared_item)
    else:
        flash(f'Item {item_name} under declaration {declaration_number} not found.', 'error')
        return redirect(url_for('main.register_imported'))
    


@views.route('/balance', methods=['GET', 'POST'])
def manage_balance():
    declared_items = Balance.query
    if request.method == 'POST':
        declaration_number = request.form.get('declaration_number')

        
        
        # Retrieve declared items matching the declaration number
        declared_items = Balance.query.filter_by(declaration_number=declaration_number).all()
        
        # If no items are found, flash a message
        if not declared_items:
          flash('No items found for the given declaration number.', 'warning')

    return render_template('balance.html', balance_items=declared_items)

from flask import request, render_template, flash
from sqlalchemy import or_


@views.route('/export_pdf')
def export_pdf():
    # Fetch all registered declarations
    declarations = Declared.query.all()

    # Create a PDF file
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Registered Declarations")

    # Set starting position for text
    x = 50
    y = 750

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(x, y, "Registered Declarations")
    y -= 30

    # Table Headers
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(x, y, "Declaration Number")
    pdf.drawString(x + 150, y, "Item Name")
    pdf.drawString(x + 250, y, "Amount of Bag")
    pdf.drawString(x + 350, y, "Bag in KG")
    pdf.drawString(x + 450, y, "Date")
    y -= 20

    # Table Content
    pdf.setFont("Helvetica", 12)
    for declaration in declarations:
        if y < 50:  # Check if we need to start a new page
            pdf.showPage()
            y = 750  # Reset y position for new page
        pdf.drawString(x, y, declaration.declaration_number)
        pdf.drawString(x + 150, y, declaration.item_name)
        pdf.drawString(x + 250, y, str(declaration.amount))
        pdf.drawString(x + 350, y, str(declaration.measurement))
        pdf.drawString(x + 450, y, str(declaration.date))
        y -= 20

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    # Create a response object with the PDF file
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=registered_declarations.pdf'

    return response

 