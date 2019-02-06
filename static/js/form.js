$(document).ready(function() {

	$('#filter').on('submit', function(event) {

		var selectedAwokenSkillIds = $('div#selected_awokenskills > button').map(function() {
			return $(this).val();
		}).get();

		$.ajax({
			data: JSON.stringify({
				MainAtt    : $('input[name=selectMainAtt]:checked').val(),
				SubAtt     : $('input[name=selectSubAtt]:checked').val(),
				Awoken     : selectedAwokenSkillIds,
				IncSuper   : $('#IncSuper').is(':checked'),
				TopN       : $('select#TopN').val()
			}),
			contentType: 'application/json;charset=UTF-8',
			type: 'POST',
			url: '/monSearch1',
		})
		.done(function(output) {

			if (output.error) {
				$('#results').text(output.error);
			}
			else {
				$('#results').html(output.Monster);
			};

			$('#results')[0].scrollIntoView();

		});

		event.preventDefault();

	});

	$('#results').on('click', 'button', function(event) {
		
		$.ajax({
			data: JSON.stringify({
				ID : $(this).find('input[type="hidden"]').val()
			}),
			contentType: 'application/json;charset=UTF-8',
			type: 'POST',
			url: '/monData',
		})
		.done(function(output) {

			if (output.error) {
				$('#monDataViewer').text(output.error);
			}
			else {
				$('#monDataViewer').html(output);
			};

			$('#monDataViewer')[0].scrollIntoView();

		});

		event.preventDefault();

	});

});