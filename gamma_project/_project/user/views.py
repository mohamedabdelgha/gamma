from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime,timedelta
from django.db.models import F
import pytz
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation, DecimalException
from django.forms.models import model_to_dict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import RecentAction , Client , Sale , Payment
from django.contrib.auth.models import User


#====================================================================================================================
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.warning(request, 'هناك خطأ في اسم المستخدم او كلمة المرور')

    return render(request, 'login.html')
#====================================================================================================================
def logout_user(request):
    logout(request)
    return render(request, 'logout.html')
#====================================================================================================================
@login_required(login_url="login")

def home(request) :
    return render(request, "home.html")
#====================================================================================================================
@login_required(login_url="login")
def sales(request):
    sale = Sale.objects.all().order_by("-date")
    clients = Client.objects.all()

    total_payments_day = Payment.objects.filter(date__date=timezone.now().date()).aggregate(Sum('paid_money'))['paid_money__sum']
    total_payments_day = total_payments_day or 0

    total_sales_day = Sale.objects.filter(date__date=timezone.now().date()).aggregate(Sum('total'))['total__sum']
    total_sales_day = total_sales_day or 0

    remain = total_sales_day - total_payments_day
    paginator = Paginator(sale ,20)
    page = request.GET.get('page')
    try:
        sale_list = paginator.page(page)
    except PageNotAnInteger:
        sale_list = paginator.page(1)
    except EmptyPage :
        sale_list = paginator.page(paginator.num_pages)

    if "addSale" in request.POST :
        client_name = request.POST.get('client')
        item = request.POST.get('item')  
        paper_num = request.POST.get('paper_num')
        copies_num = request.POST.get('copies_num')
        price = request.POST.get('price')
        paid = request.POST.get('paid')
        remain = request.POST.get('remain')

        client_name = client_name.strip()

        paper_num = Decimal(paper_num)
        copies_num = Decimal(copies_num)
        price = Decimal(price)
        paid = Decimal(paid)
        remain = Decimal(remain)

        if price == 0 :
            messages.warning(request, "السعر اقل من صفر")
        if not paid :
            paid = 0
        
        client = None  

        try:
            client = Client.objects.get(name=client_name)
        except Client.DoesNotExist:
            messages.warning(request, f"اسم العميل ({client_name}) غير موجود   ")
            return redirect("sales")

        if client is not None and paid is not None :
            new_sale = Sale.objects.create(client=client, item=item, paper_num=paper_num , copies_num = copies_num, price= price , remain = remain, paid= paid)
            new_payment = Payment.objects.create(client=client, paid_money=paid)
            RecentAction.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='عملية بيع',
                action_sort = 'بيع',
                model_affected=f'تم اضافة عملية بيع  للعميل ({new_sale.client.name}) من الصنف ({new_sale.item}) و بإجمالي ({new_sale.total} جنيه)',
            )
            RecentAction.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='عملية دفع',
                action_sort = 'دفع',
                model_affected=f'تم اضافة عملية دفع  للعميل ({new_payment.client.name}) بإجمالي ({new_payment.paid_money} جنيه)',
            )

            messages.success(request, "تمت إضافة عملية بيع بنجاح")
            return redirect("sales")
        
        if client is not None :
            new_sale = Sale.objects.create(client=client, item=item, paper_num=paper_num , copies_num = copies_num, price= price )
            RecentAction.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='عملية بيع',
                action_sort = 'بيع',
                model_affected=f'تم اضافة عملية بيع  للعميل ({new_sale.client.name}) من الصنف ({new_sale.item}) و بإجمالي ({new_sale.total} جنيه)',
            )

            messages.success(request, "تمت إضافة عملية بيع بنجاح")
            return redirect("sales")
    
    elif 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Sale.objects.all().filter(Q(client__name__icontains=search_input)).values()]
        sale_list = [Sale.objects.get(pk = id) for id in results]

    
    context ={
        "sales" : sale_list,
        "clients" : clients,
        "total_payments_day" : total_payments_day,
        "total_sales_day" : total_sales_day,
        "remain" : remain,
    }
    return render(request, 'index.html', context)
#====================================================================================================================
def sale_update(request, id):
    old_sale_data = Sale.objects.values().get(id=id)

    if "saleUpdate" in request.POST:
        client = request.POST["client"]
        item = request.POST["item"]
        paper_num = request.POST["paper_num"]
        copies_num = request.POST["copies_num"]
        price = request.POST["price"]

        paper_num = Decimal(paper_num)
        copies_num = Decimal(copies_num)
        price = Decimal(price)
        client = client.strip()
        try:
            client_obj = Client.objects.get(name=client)
        except Client.DoesNotExist:
            messages.warning(request, f"اسم العميل ({client}) غير موجود   ")
            return redirect("sales")

        edit = Sale.objects.get(id=id)

        old_client = old_sale_data["client_id"]
        old_item = old_sale_data["item"]
        old_paper_num = old_sale_data["paper_num"]
        old_copies_num = old_sale_data["copies_num"]
        old_price = old_sale_data["price"]

        changes = []
        if client_obj.id != old_client:
            changes.append(f'اسم العميل من {Client.objects.get(id=old_client).name} إلى {client_obj.name}')
        if item != old_item:
            changes.append(f'نوع العملية من {old_item} إلى {item}')
        if str(paper_num) != str(old_paper_num):
            changes.append(f'عدد الورق من {old_paper_num} إلى {paper_num}')
        if str(copies_num) != str(old_copies_num):
            changes.append(f'عدد النسخ من {old_copies_num} إلى {copies_num}')
        if str(price) != str(old_price):
            changes.append(f'السعر من {old_price} إلى {price}')

        edit.client = client_obj
        edit.item = item
        edit.paper_num = paper_num
        edit.copies_num = copies_num
        edit.price = price
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل عملية',
            action_sort = 'تعديل',
            model_affected=f'تم تعديل بيانات العملية: {", ".join(changes)}',
        )
        messages.success(request, 'تم تعديل بيانات العملية بنجاح', extra_tags='success')
        return redirect("sales")
      
#====================================================================================================================
def sale_delete(request, id):
    sale_to_delete = get_object_or_404(Sale, id =id )
    client_id = sale_to_delete.client.id

    if "saleDelete" in request.POST :
        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='حذف عملية بيع',
            action_sort = 'حذف',
            model_affected=f'تم حذف عملية بيع للعميل ({sale_to_delete.client.name})',
        )
        sale_to_delete.delete()
        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("sales")
    
    elif "saleDelete2" in request.POST :
        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='حذف عملية بيع',
            action_sort = 'حذف',
            model_affected=f'تم حذف عملية بيع للعميل ({sale_to_delete.client.name})',
        )
        sale_to_delete.delete()
        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("clientpage", id= client_id)
#====================================================================================================================
@login_required(login_url="login")
def clients(request):
    client = Client.objects.all().order_by("-date")
    paginator = Paginator(client ,20)
    page = request.GET.get('page')
    try:
        client_list = paginator.page(page)
    except PageNotAnInteger:
        client_list = paginator.page(1)
    except EmptyPage :
        client_list = paginator.page(paginator.num_pages)

    if "addClient" in request.POST :
        name = request.POST.get('name')
        opening_balance = request.POST.get('opening_balance')  
        phone = request.POST.get('phone')
        notes = request.POST.get('notes')
        date = request.POST.get('date')

        name = name.strip()

        if not opening_balance:
            opening_balance = 0
        if not phone:
            phone = None
        if not notes:
            notes = "-"

        if Client.objects.filter(name=name).exists():
            messages.warning(request, f'اسم العميل ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect('clients')
        
        new_client = Client.objects.create(name=name, opening_balance=opening_balance, date=date , phone = phone, notes= notes )
        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='إضافة عميل جديد',
            action_sort = 'اضافة',
            model_affected=f'تم إضافة عميل جديد باسم ({new_client.name}) برصيد افتتاحي قدره ({new_client.opening_balance} جنيها)',
        )

        messages.success(request, 'تم إضافة عميل جديد بنجاح', extra_tags='success')
        return redirect('clients')
    
    elif 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Client.objects.all().filter(Q(name__icontains=search_input)).values()]
        client_list = [Client.objects.get(pk = id) for id in results]


    context = {"clients" : client_list}
    return render(request,"clients.html", context)
#====================================================================================================================
def client_update(request, id):
    old_client_data = None

    if 'clientUpdate' in request.POST:
        name = request.POST['name']
        phone = request.POST['phone']
        notes = request.POST['notes']
        opening_balance = request.POST['opening_balance']

        name = name.strip()

        old_client_data = Client.objects.filter(id=id).values().first()

        if Client.objects.filter(name=name).exclude(id=id).exists():
            messages.warning(request, f'اسم العميل ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect("clientpage", id=id)
        
        edit = Client.objects.get(id=id)
        old_name = old_client_data["name"]
        old_opening_balance = old_client_data["opening_balance"]
        old_phone = old_client_data["phone"]

        changes = []
        if name != old_name:
            changes.append(f'اسم العميل من {old_name} إلى {name}')
        if str(opening_balance) != str(old_opening_balance):
            changes.append(f'رصيد الافتتاح من {old_opening_balance} إلى {opening_balance}')
        if str(phone) != str(old_phone):
            changes.append(f'رصيد الافتتاح من {old_phone} إلى {phone}')

        edit.name = name
        edit.phone = phone
        edit.opening_balance = opening_balance
        edit.notes = notes
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل عميل',
            action_sort = 'تعديل',
            model_affected=f'تم تعديل بيانات العميل: {", ".join(changes)}',
        )
        messages.success(request, 'تم تعديل بيانات العميل بنجاح', extra_tags='success')
        return redirect("clients")
    
#====================================================================================================================
def client_delete(request, id):
    client_to_delete = get_object_or_404(Client, id =id )

    if "clientDelete" in request.POST :
        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='حذف عميل',
            action_sort = 'حذف',
            model_affected=f'تم حذف العميل ({client_to_delete.name})',
        )
        client_to_delete.delete()
        messages.success(request, "تم حذف العميل بنجاح")
        return redirect("clients")
#====================================================================================================================
@login_required(login_url="login")
def client_page(request, id):
    client = get_object_or_404(Client, id=id)
    sales = Sale.objects.filter(client=client).order_by("-date")
    payments = Payment.objects.filter(client=client).order_by('-date')

    context = {"client": client, "sales": sales, "payments"  : payments}
    return render(request, "clientpage.html", context)
#====================================================================================================================
@login_required(login_url="login")
def profits(request):
    payments = Payment.objects.all().order_by("-date")
    paginator = Paginator(payments ,20)
    page = request.GET.get('page')
    try:
        payment_list = paginator.page(page)
    except PageNotAnInteger:
        payment_list = paginator.page(1)
    except EmptyPage :
        payment_list = paginator.page(paginator.num_pages)

    if "addpay" in request.POST :
        client_name = request.POST.get('client')
        paid_money = request.POST.get('paid_money') 
        paid_money = Decimal(paid_money)

        client_name = client_name.strip()
        client = None  



        try:
            client = Client.objects.get(name=client_name)
        except Client.DoesNotExist:
            messages.warning(request, f"اسم العميل ({client_name}) غير موجود   ")
            return redirect("profits")
        if client is not None:
            new_payment = Payment.objects.create(client=client, paid_money=paid_money )
            RecentAction.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='عملية دفع',
                action_sort = 'دفع',
                model_affected=f'تم اضافة عملية دفع  للعميل ({new_payment.client.name}) بإجمالي ({new_payment.paid_money} جنيه)',
            )

            messages.success(request, "تمت إضافة عملية دفع بنجاح")
            return redirect("profits")
        
    elif 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Payment.objects.all().filter(Q(client__name__icontains=search_input)).values()]
        payment_list = [Payment.objects.get(pk = id) for id in results]

        
    clients = Client.objects.all()
    context ={
        "pays" : payment_list,
        "clients" : clients,
    }
    return render(request,"profits.html", context)
#====================================================================================================================
def pay_update(request, id):
    old_pay_data = Payment.objects.values().get(id=id)

    if "payupdate" in request.POST:
        client = request.POST["client"]
        paid_money = request.POST["paid_money"]

        client = client.strip()

        paid_money = Decimal(paid_money)

        try:
            client_obj = Client.objects.get(name=client)
        except Client.DoesNotExist:
            messages.warning(request, f"اسم العميل ({client}) غير موجود   ")
            return redirect("profits")

        edit = Payment.objects.get(id=id)

        old_client = old_pay_data["client_id"]
        old_paid_money = old_pay_data["paid_money"]

        changes = []
        if client_obj.id != old_client:
            changes.append(f'اسم العميل من {Client.objects.get(id=old_client).name} إلى {client_obj.name}')
        if str(paid_money) != str(old_paid_money):
            changes.append(f'السعر من {old_paid_money} إلى {paid_money}')

        edit.client = client_obj
        edit.paid_money = paid_money
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل استلام نقدية',
            action_sort = 'تعديل',
            model_affected=f'تم تعديل عملية استلام نقدية: {", ".join(changes)}',
        )
        messages.success(request, 'تم تعديل بيانات التحصيل بنجاح', extra_tags='success')
        return redirect("profits")

#====================================================================================================================
def pay_delete(request, id):
    pay_to_delete = get_object_or_404(Payment, id =id )
    client_id = pay_to_delete.client.id

    if "paydelete" in request.POST :
        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='حذف عملية دفع',
            action_sort = 'حذف',
            model_affected=f'تم حذف عملية دفع للعميل ({pay_to_delete.client.name}) و كانت بقيمة ({pay_to_delete.paid_money})',
        )
        pay_to_delete.delete()
        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("profits")
#====================================================================================================================
@login_required(login_url="login")
def adminPage(request):
    if "addUser" in request.POST :
        username = request.POST.get('username')
        password = request.POST.get('password')
        firstname = request.POST.get('firstname')

        username = username.strip()

        if not firstname :
            messages.warning(request,"يرجى ادخال نوع الصلاحية")
            return redirect('adminPage')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم موجود بالفعل')
            return redirect('adminPage')

        User.objects.create_user(username=username, password=password, first_name=firstname)
        messages.success(request, 'تم تسجيل مستخدم جديد بنجاح')
        return redirect('adminPage')
    context = {
        'users': User.objects.all()
    }

    return render(request,"admin.html",context)
#====================================================================================================================
def user_delete(request, id):
    user_to_delete = get_object_or_404(User, id=id)
    if "deleteUser" in request.POST :
        user_to_delete.delete()
        messages.success(request, "تم حذف المستخدم بنجاح")
        return redirect("adminPage")
#====================================================================================================================
@login_required(login_url="login")    
def reports(request):

    if "reportsShow" in request.POST:
        date_str = request.POST.get('date')
        try:
            selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'تاريخ غير صالح')
            return redirect('reports')

        recent_actions = RecentAction.objects.filter(timestamp__date=selected_date)
        return render(request, 'reports.html', {
            'recent_actions': recent_actions,
            'selected_date' : selected_date,
        })

    return render(request, 'reports.html')

#====================================================================================================================

