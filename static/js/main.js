document.addEventListener("DOMContentLoaded", function () {

    const department = document.getElementById("department");
    const program = document.getElementById("program");
    const course = document.getElementById("course");
    const classSelect = document.getElementById("class");
    const section = document.getElementById("section");

    department.addEventListener("change", function () {
        fetch(`/academics/get-programs/?department_id=${this.value}`)
            .then(res => res.json())
            .then(data => {
                program.innerHTML = '<option value="">Select Program</option>';
                data.forEach(item => {
                    program.innerHTML += `<option value="${item.id}">${item.name}</option>`;
                });
            });
    });

    program.addEventListener("change", function () {
        fetch(`/academics/get-courses/?program_id=${this.value}`)
            .then(res => res.json())
            .then(data => {
                course.innerHTML = '<option value="">Select Course</option>';
                data.forEach(item => {
                    course.innerHTML += `<option value="${item.id}">${item.name}</option>`;
                });
            });
    });

    course.addEventListener("change", function () {
        fetch(`/academics/get-classes/?course_id=${this.value}`)
            .then(res => res.json())
            .then(data => {
                classSelect.innerHTML = '<option value="">Select Class</option>';
                data.forEach(item => {
                    classSelect.innerHTML += `<option value="${item.id}">${item.name}</option>`;
                });
            });
    });

    classSelect.addEventListener("change", function () {
        fetch(`/academics/get-sections/?class_id=${this.value}`)
            .then(res => res.json())
            .then(data => {
                section.innerHTML = '<option value="">Select Section</option>';
                data.forEach(item => {
                    section.innerHTML += `<option value="${item.id}">${item.name}</option>`;
                });
            });
    });

});