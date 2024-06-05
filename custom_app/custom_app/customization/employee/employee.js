frappe.ui.form.on("Employee", {
	validate(frm) {
		custom_app.employee.validate_salary_mode(frm.doc.salary_mode);
	},
});
