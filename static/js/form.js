var baseurl = window.location.pathname;

function populateDataViewer(el){

	$.ajax({
		data: JSON.stringify({
			ID : $(el).val()
		}),
		contentType: 'application/json;charset=UTF-8',
		type: 'POST',
		url: baseurl + 'monData',
	})
	.done(function(output) {

		if (output.error) {
			$('#monDataViewer').text(output.error);
		}
		else {
			$('#monDataViewer').html(output);
		};

	});

}


$(document).ready(function() {

    $('div#selected_awokenskills').on('click', 'button', function() {
      $(this).remove();
    });

    $('button#ClearAwokenSkill').click(function() {
      $('div#selected_awokenskills').empty();
    });

    $('select#IncSuper').selectpicker('setStyle', 'btn-default btn-sm');


    $('#EnableRange').change(function() {
      if (this.checked) {
        $('#ToId').prop('disabled', false);
        $('#FromId').attr('placeholder', 'From');
        $('#ToId').attr('placeholder', 'To');
      } else {
        $('#ToId').prop('disabled', true);
        $('#FromId').attr('placeholder', 'ID');
        $('#ToId').attr('placeholder', '');
      };
    });


	$('#filter').on('submit', function(event) {

		var selectedAwokenSkillIds = $('div#selected_awokenskills > button').map(function() {
			return $(this).val();
		}).get();

		var selectedTypes = $('div#Type').find('input[type=checkbox]:checked').map(function() {
			return $(this).val();
		}).get();

		var selectedActiveSkillTypes = $('div#ActiveSkill').find('input[type=checkbox]:checked').map(function() {
			return $(this).val();
		}).get();

		$.ajax({
			data: JSON.stringify({
				MainAtt    : $('input[name=selectMainAtt]:checked').val(),
				SubAtt     : $('input[name=selectSubAtt]:checked').val(),
				Type       : selectedTypes,
				Awoken     : selectedAwokenSkillIds,
				IncSuper   : $('#IncSuper').val(),
				Active     : selectedActiveSkillTypes,
				Assistable : $('#checkAssistable').prop("checked"),
				SortBy     : $('select#SortBy').val(),
				TopN       : $('select#TopN').val()
			}),
			contentType: 'application/json;charset=UTF-8',
			type: 'POST',
			url: baseurl + 'monSearch1',
		})
		.done(function(output) {

			if (output.error) {
				$('#results').text(output.error);
			}
			else {
				$('#results').html(output.Monster);
				populateDataViewer($('#results > button')[0]);
			};

			$('#results')[0].scrollIntoView();

		});

		event.preventDefault();

	});


	$('#filter').on('reset', function(event) {

		$('button.active').removeClass('active');

		$('input[name=selectMainAtt][value=Any]').parent('button').addClass('active');

		$('input[name=selectSubAtt][value=Any]').parent('button').addClass('active');

		$('div#selected_awokenskills').empty();

		var _this = this;
		setTimeout(function() {
			$('.selectpicker', _this).selectpicker('refresh');
		})

	});


	$('#FormId').on('submit', function(event) {

		$.ajax({
			data: JSON.stringify({
				FromId    : $('#FromId').val(),
				ToId      : $('#ToId').val()
			}),
			contentType: 'application/json;charset=UTF-8',
			type: 'POST',
			url: baseurl + 'monSearch2',
		})
		.done(function(output) {

			if (output.error) {
				$('#results').text(output.error);
			}
			else {
				$('#results').html(output.Monster);
				populateDataViewer($('#results > button')[0]);
			};

			$('#results')[0].scrollIntoView();

		});

		event.preventDefault();

	});


	$('#results').on('click', '.btn-monster', function(event) {

		populateDataViewer($(this));

		$('#monDataViewer')[0].scrollIntoView();

	});

	$('#monDataViewer').on('click', '.btn-monster', function(event) {

		populateDataViewer($(this));

	});

});
