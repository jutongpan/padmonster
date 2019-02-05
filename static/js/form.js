$(document).ready(function() {

	$('#filter').on('submit', function(event) {

		$.ajax({
			data: {
				'MainAtt' : $('input[name=selectMainAtt]:checked').val(),
				'SubAtt'  : $('input[name=selectSubAtt]:checked').val(),
				'TopN'    : $('select#TopN').val()
			},
			type: 'POST',
			url: '/monSearch1',
		})
		.done(function(output) {

			if (output.error) {
				$('#results').text(output.error);
			}
			else {
				$('#results').html(output.Monster);
			}

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
			}

		});

		event.preventDefault();

	});

});