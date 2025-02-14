document.addEventListener('DOMContentLoaded', function() {
    const groupSelect = document.querySelector('select[name="groups"]');
    const usersList = document.getElementById('users-list');
    const searchUserInput = document.getElementById('search-user-input');
    const searchResults = document.getElementById('search-results');
    const additionalRecipientsList = document.getElementById('additional-recipients-list');

    groupSelect.addEventListener('change', function() {
        const selectedGroups = Array.from(groupSelect.selectedOptions).map(option => option.value);
        if (selectedGroups.length > 0) {
            fetch(`/group_users?group_ids=${selectedGroups.join(',')}`)
                .then(response => response.json())
                .then(data => {
                    usersList.innerHTML = '';
                    data.forEach(user => {
                        const userCheckbox = document.createElement('div');
                        userCheckbox.classList.add('form-check');
                        userCheckbox.innerHTML = `
                            <input class="form-check-input" type="checkbox" value="${user.id}" name="recipients" checked>
                            <label class="form-check-label">${user.username}</label>
                        `;
                        usersList.appendChild(userCheckbox);
                    });
                });
        } else {
            usersList.innerHTML = '';
        }
    });

    searchUserInput.addEventListener('input', function() {
        const query = searchUserInput.value.trim();
        if (query.length > 0) {
            fetch(`/search_users?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    searchResults.innerHTML = '';
                    data.forEach(user => {
                        const userItem = document.createElement('a');
                        userItem.classList.add('list-group-item', 'list-group-item-action');
                        userItem.textContent = user.username;
                        userItem.href = '#';
                        userItem.addEventListener('click', function(e) {
                            e.preventDefault();
                            const userCheckbox = document.createElement('div');
                            userCheckbox.classList.add('form-check');
                            userCheckbox.innerHTML = `
                                <input class="form-check-input" type="checkbox" value="${user.id}" name="additional_recipients" checked>
                                <label class="form-check-label">${user.username}</label>
                            `;
                            additionalRecipientsList.appendChild(userCheckbox);
                            searchUserInput.value = '';
                            searchResults.innerHTML = '';
                        });
                        searchResults.appendChild(userItem);
                    });
                });
        } else {
            searchResults.innerHTML = '';
        }
    });
});