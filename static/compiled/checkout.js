var stripe;var orderData={items:[{id:"photo-subscription"}],currency:"usd"};let url="http://localhost:5000";fetch(url+"/api/create-payment-intent",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(orderData)}).then(function(result){return result.json();}).then(function(data){return setupElements(data);}).then(function({stripe,card,clientSecret,intentId}){document.querySelector("button").disabled=false;var form=document.getElementById("payment-form");form.addEventListener("submit",function(event){event.preventDefault();pay(stripe,card,clientSecret,intentId);});});var setupElements=function(data){stripe=Stripe(data.publishableKey);var elements=stripe.elements();var style={base:{color:"#32325d",fontFamily:'"Helvetica Neue", Helvetica, sans-serif',fontSmoothing:"antialiased",fontSize:"16px","::placeholder":{color:"#aab7c4"}},invalid:{color:"#fa755a",iconColor:"#fa755a"}};var card=elements.create("card",{style:style});card.mount("#card-element");return{stripe:stripe,card:card,clientSecret:data.clientSecret,intentId:data.intentId};};var pay=function(stripe,card,clientSecret,intentId){changeLoadingState(true);stripe.confirmCardPayment(clientSecret,{payment_method:{card:card}}).then(function(result){if(result.error){showError(result.error.message);}else{orderComplete(clientSecret,intentId);}});};var orderComplete=function(clientSecret,intentId){$.post(url+'/api/handle-payment',{intentId:intentId})};var showError=function(errorMsgText){var errorMsg=document.querySelector(".sr-field-error");errorMsg.textContent=errorMsgText;setTimeout(function(){errorMsg.textContent="";},4000);};var changeLoadingState=function(state){};