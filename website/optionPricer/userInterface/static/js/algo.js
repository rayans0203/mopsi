(function() { 

			var paramForm = document.getElementById('paramForm'),
				inputs = document.querySelectorAll('input[type=text], input[type=password]'),
				inputsLength = inputs.length;

			for (var i = 0; i < inputsLength; i++) {
				inputs[i].addEventListener('keyup', function(e) {
				});
			}
			
			// il faut prevoir des fonction qui verifie les types entres
			
			paramForm.addEventListener('submit', function(e) {
				var Stock=document.getElementById('Stock').value;
				//var Order=document.getElementById('Order').value;
				//var Model=document.getElementById('Model').value;
				//var Strike=document.getElementById('Strike').value;
				//var Maturity=document.getElementById('Maturity').value;
				//var Volatility=document.getElementById('Volatility').value;
				//var Accuracy=document.getElementById('Accuracy').value;
				//var InterestRates=document.getElementById('InterestRates').value;
				
				document.getElementById("callPrice").innerHTML = Stock; // pb de somme
				
				e.preventDefault();
			});
		
			paramForm.addEventListener('reset', function() {
				for (var i = 0; i < inputsLength; i++) {
				inputs[i].className = '';
				}
			});
		})();