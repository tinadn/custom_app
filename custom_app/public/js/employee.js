frappe.provide("custom_app.employee");

custom_app.employee.validate_salary_mode = function (salary_mode) {
        if(salary_mode == "Cheque")
            frappe.throw(__("Salary mode Cheque is not available."))
};
