document.addEventListener('DOMContentLoaded', function () {
  const targetField = document.getElementById('id_target');
  const facultyField = document.getElementById('id_faculty');
  const departmentField = document.getElementById('id_department');

  function toggleFields() {
    const value = targetField.value;

    if (value === 'all') {
      facultyField.disabled = true;
      departmentField.disabled = true;
    } else if (value === 'faculty') {
      facultyField.disabled = false;
      departmentField.disabled = true;
    } else if (value === 'department') {
      facultyField.disabled = false;
      departmentField.disabled = false;
    } else {
      facultyField.disabled = true;
      departmentField.disabled = true;
    }
  }

  // Initial toggle
  toggleFields();

  // On change
  targetField.addEventListener('change', toggleFields);
});
