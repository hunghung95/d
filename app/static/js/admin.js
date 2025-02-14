$(document).ready(function(){
    $('#group-select').change(function(){
        var groupId = $(this).val();
        if(groupId){
            $.ajax({
                url: '/group_users/' + groupId,
                type: 'GET',
                success: function(data){
                    var userSelect = $('#user-select');
                    userSelect.empty();
                    data.forEach(function(user){
                        userSelect.append('<div class="form-check"><input class="form-check-input" type="checkbox" value="' + user.id + '" name="recipients"><label class="form-check-label">' + user.username + '</label></div>');
                    });
                    userSelect.append('<div class="form-check"><input class="form-check-input" type="checkbox" id="select-all"><label class="form-check-label">Chọn tất cả</label></div>');
                }
            });
        } else {
            $('#user-select').empty();
        }
    });

    $(document).on('change', '#select-all', function(){
        var checked = this.checked;
        $('input[name="recipients"]').each(function(){
            this.checked = checked;
        });
    });
});