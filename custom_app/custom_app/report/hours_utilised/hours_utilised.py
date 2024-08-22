# Copyright (c) 2024, Tina and contributors
# For license information, please see license.txt
from datetime import timedelta
from erpnext.accounts.utils import get_fiscal_year
from frappe import _, scrub
from frappe.query_builder.utils import DocType
from frappe.query_builder.functions import Sum
import frappe
from frappe.utils.data import add_days, add_to_date, getdate


def execute(filters=None):
	columns, data = [], []
	columns = get_column(filters)
	data = get_data(filters)
	return columns, data

def get_column(filters):
	columns = [
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 180,
		},
		{
			"label": _("Project"),
			"fieldname": "project",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Total Hours"),
			"fieldname": "hours",
			"fieldtype": "Data",
			"width": 120,
		},
		
	]
	start_date = None
	periodic_daterange = get_period_date_ranges(filters)
	for end_date in periodic_daterange:
		if(start_date):
			period = get_period(filters, end_date)
			columns.append(
				{"label": _(period), "fieldname": scrub(period), "fieldtype": "Int", "width": 120}
			)
		start_date = end_date
	return columns

def get_data(filters):
	data=[]
	# print("SELECT t.employee, details.project, SUM(details.hours) FROM `tabTimesheet` AS t JOIN `tabTimesheet Detail` AS details ON t.name = details.parent Where t.start_date between "+str(filters.get("from_date"))+" and "+ str(filters.get("to_date")) +  get_condition(filters)+" group by t.employee, details.project " )
	print(f"""
		SELECT 
			t.employee, 
			details.project, 
			SUM(details.hours) 
		FROM 
			`tabTimesheet` AS t 
		JOIN `tabTimesheet Detail` AS details 
		ON t.name = details.parent 
		JOIN `tabEmployee` AS emp 
		ON t.employee = emp.name 
		Where emp.reports_to = {filters.get("reports_to")} {get_condition(filters)} AND (t.start_date between {filters.get("from_date")} and {filters.get("to_date")}) 
		group by t.employee, details.project;
	""")
	data2 = frappe.db.sql("""
		SELECT 
			t.employee, 
			details.project, 
			SUM(details.hours) 
		FROM 
			`tabTimesheet` AS t 
		JOIN `tabTimesheet Detail` AS details 
		ON t.name = details.parent 
		JOIN `tabEmployee` AS emp 
		ON t.employee = emp.name 
		Where emp.reports_to = %s %s AND (t.start_date between %s and %s) 
		group by t.employee, details.project;
	""",(filters.get("reports_to"),get_condition(filters), filters.get("from_date"),filters.get("to_date")), as_dict=0)
	print(data2)
	
	data=[]
	for d in data2:
		row={}
		row['employee']=d[0]
		row['project']=d[1]
		row['hours']=d[2]
		
		start_date = None
		periodic_daterange = get_period_date_ranges(filters)
		for end_date in periodic_daterange:
			if(start_date):
				start_date = start_date + timedelta(days=1)
				data3 = frappe.db.sql("""
					SELECT 
						SUM(details.hours)
					FROM 
						`tabTimesheet` AS t 
					JOIN `tabTimesheet Detail` AS details 
					ON t.name = details.parent 
					JOIN `tabEmployee` AS emp 
					ON t.employee = emp.name 
					Where t.start_date between %s and %s AND t.employee = %s AND details.project = %s
					group by t.employee, details.project;
				""",(start_date,end_date,d[0],d[1]), as_dict=0)
				if(data3):
					period = get_period(filters, end_date)
					row[scrub(period)]=data3[0][0]
			start_date = end_date
		data.append(row)
	return data

def get_condition(filters):
	condition =""
	if(filters.get("employee") and filters.get("project")):
		condition = "AND t.employee = "+ filters.get("employee")+" AND details.project = " + filters.get("project")
	if(filters.get("employee") and not filters.get("project")):
		condition = "AND t.employee = "+ filters.get("employee")
	if(not filters.get("employee") and filters.get("project")):
		condition = "AND details.project = " + filters.get("project")
	return condition

def get_period_date_ranges(filters):
		from dateutil.relativedelta import MO, relativedelta

		from_date, to_date = getdate(filters.get("from_date")), getdate(filters.get("to_date"))

		increment = {"Monthly": 1, "Quarterly": 3, "Half-Yearly": 6, "Yearly": 12}.get(filters.get("range"), 1)

		if filters.get("range") in ["Monthly", "Quarterly"]:
			from_date = from_date.replace(day=1)
		elif filters.get("range") == "Yearly":
			from_date = get_fiscal_year(from_date)[1]
		else:
			from_date = from_date + relativedelta(from_date, weekday=MO(-1))

		periodic_daterange = []
		for _dummy in range(1, 53):
			if filters.get("range") == "Weekly":
				period_end_date = add_days(from_date, 6)
			else:
				period_end_date = add_to_date(from_date, months=increment, days=-1)

			if period_end_date > to_date:
				period_end_date = to_date

			periodic_daterange.append(period_end_date)

			from_date = add_days(period_end_date, 1)
			if period_end_date == to_date:
				break
		return periodic_daterange

def get_period(filters, date):
		months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

		if filters.get("range") == "Weekly":
			period = "Week " + str(date.isocalendar()[1])
		elif filters.get("range") == "Monthly":
			period = str(months[date.month - 1])
		elif filters.get("range") == "Quarterly":
			period = "Quarter " + str(((date.month - 1) // 3) + 1)
		# else:
		# 	year = get_fiscal_year(date, self.filters.company)
		# 	period = str(year[0])

		if (
			getdate(filters.get("from_date")).year != getdate(filters.get("to_date")).year
			and filters.get("range") != "Yearly"
		):
			period += " " + str(date.year)

		return period

