// Copyright (c) 2024, Tina and contributors
// For license information, please see license.txt

frappe.query_reports["Hours utilised"] = {
	"filters": [
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			reqd: 0,
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
			reqd: 0,
		},
		{
			fieldname: "reports_to",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			// default: frappe.defaults.get_global_default("year_start_date"),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			// default: frappe.defaults.get_global_default("year_end_date"),
			reqd: 1,
		},
		{
			fieldname: "range",
			label: __("Date Range"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("") },
				{ value: "Weekly", label: __("Weekly") },
				{ value: "Monthly", label: __("Monthly") },
				{ value: "Quarterly", label: __("Quarterly") },
				{ value: "Yearly", label: __("Yearly") },
			],
			default: "Weekly",
			reqd: 0,
		},
	]
};
