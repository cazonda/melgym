document.addEventListener('DOMContentLoaded', () => {
  const element = document.querySelector('#punch');
  if(element){
    element.addEventListener('click', () => {
      punch_member(element.dataset.id)
    });
  }
  
  const member_memberships_btn = document.querySelector('#member_memberships')
  if(member_memberships_btn){
    member_memberships_btn.addEventListener('click', ()=>{
      display_member_memberships(member_memberships_btn.dataset.id)
    });
  }  

  document.querySelectorAll('#pay-membership').forEach(btn => {
    btn.onclick = () => displayPay(btn.dataset.id)
  })
})

function displayPay(id){
  //document.querySelector('#head').style.display = 'none'
  //document.querySelector('#card-profile').style.display = 'none'
  document.querySelector('#member-details').innerHTML =
    `
    <form action="" id="pay-membership-form" onsubmit="return false">      
    <div class="row">
      <div class="col-sm-3">
        <label><strong>Amount</strong></label>
      </div>
      <div class="col-sm-9">
        <input type="number" min="0.00" step="0.01" class="form-control" id="payment-amount">
      </div>
    </div>
    <hr>
    <div class="row">
      <div class="col-sm-3">
        <label><strong>Discount</strong></label>
      </div>
      <div class="col-sm-9">
        <input type="number" min="0.00" step="0.01" type="text"  class="form-control" id="payment-discount">
      </div>
    </div>
    <hr>   
    <input type="submit"  value ="Pay" class="btn btn-dark btn-sm">
  </form>`
  document.querySelector('#pay-membership-form').addEventListener('submit', () => payMembership(id))
}

function payMembership(id){
  let csrftoken = getCookie('csrftoken');

  const paid_amount = document.querySelector('#payment-amount').value;
  const  discount = document.querySelector('#payment-discount').value;

  fetch('/pay-membership', {
    method: 'POST',
    body: JSON.stringify({
      id: id,
      discount: discount,
      paid_amount: paid_amount,
    }),
    headers: { "X-CSRFToken": csrftoken },
  })
  window.location.reload(`${id}`);
}

function display_edit(id) {
  const email = document.querySelector('#member-email').innerHTML
  const phone = document.querySelector('#member-phone').innerHTML
  const age = document.querySelector('#member-age').innerHTML
  const address = document.querySelector('#member-address').innerHTML

  document.querySelector('#head').style.display = 'none'
  document.querySelector('#card-profile').style.display = 'none'

  document.querySelector('#member-details').innerHTML =
    `
    <h2 style="text-align: center;">Edit Member Detail</h2>

    <form action="" id="edit-form" onsubmit="return false">
      
    <div class="row">
      <div class="col-sm-3">
        <p class="mb-0">Email</p>
      </div>
      <div class="col-sm-9">
        <input type="text" value="${email}" class="form-control" id="member-email">
      </div>
    </div>
    <hr>
    <div class="row">
      <div class="col-sm-3">
        <p class="mb-0">Phone Number</p>
      </div>
      <div class="col-sm-9">
        <input type="text"  value="${phone}" class="form-control" id="member-phone">
      </div>
    </div>
    <hr>
    <div class="row">
      <div class="col-sm-3">
        <p class="mb-0">Age</p>
      </div>
      <div class="col-sm-9">
        <input type="text"  value="${age}" class="form-control" id="member-age">
      </div>
    </div>
    <hr>   
    <div class="row">
      <div class="col-sm-3">
        <p class="mb-0">Address</p>
      </div>
      <div class="col-sm-9">
        <input type="text" value="${address}" class="form-control" id="member-address">
      </div>
    </div>
    <hr>
   
    <input type="submit"  value ="Edit" class="btn btn-primary btn-sm">

</form>`
  document.querySelector('#edit-form').addEventListener('submit', () => editMember(id))

}


function editMember(id) {

  let csrftoken = getCookie('csrftoken');

  const email = document.querySelector('#member-email').value
  const phone = document.querySelector('#member-phone').value
  const age = document.querySelector('#member-age').value
  const address = document.querySelector('#member-address').value

  fetch('/edit', {
    method: 'POST',
    body: JSON.stringify({
      id: id,
      email: email,
      phone: phone,
      age: age,
      address: address,
    }),
    headers: { "X-CSRFToken": csrftoken },

  })
  window.location.reload(`${id}`);
}


function punch_member(id) {

  let csrftoken = getCookie('csrftoken');

  fetch('/punch-member', {
    method: 'POST',
    body: JSON.stringify({
      id: id,
    }),
    headers: { "X-CSRFToken": csrftoken },
  })
  window.location.reload(`${id}`);
}


function display_member_memberships(id){
  document.querySelector('#head').style.display = 'none'
  document.querySelector('#card-profile').style.display = 'none'

  document.querySelector('#member-details').innerHTML =
    `
      <h2 style="text-align: center;">Member Memberships</h2>
      <table class="table table-hover">
          <tr>
              <th>Membership</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Status</th>        
          </tr>
          {% for membership in page_obj %} 
              <tr>
                <td>{{membership.first_name}}</a></td>
                <td>{{membership.last_name}}</a></td>
                <td>{{membership.phone_number}}</td>
                <td>{{membership.phone_number}}</td>
              </tr>
              {% empty %}
              <p>No results to show</p>
          {% endfor %}
      </table>
    `
}

/*function display_renew(id) {
  document.querySelector('#head').style.display = 'none'
  document.querySelector('#card-profile').style.display = 'none'

  document.querySelector('#member-details').innerHTML =
    `
    <h2 style="text-align: center;">Renew Membership </h2>
    <form action="" id="renew-form" onsubmit="return false">
      <div class="form-group">
        <select class="form-control" name="cars" id="cars">
          <option value="volvo">Volvo</option>
          <option value="saab">Saab</option>
          <option value="mercedes">Mercedes</option>
          <option value="audi">Audi</option>
        </select>      
      </div>
      <div class="form-group">  
        <input type="input" placeholder="Paid Amount"  class="form-control" id="valid-date">
      </div>
      <div class="form-group">
        <input type="input" placeholder="Discount" class="form-control" id="valid-date">
      </div>
      <div class="form-group">
        <input type="input" placeholder="Due Amount" class="form-control" id="valid-date">
      </div>
      <div class="form-group">
        <input type="date" placeholder="Valid Until" class="form-control" id="valid-date">
      </div>
      <div class="form-group">
        <input type="submit"  value ="Renew" class="btn btn-dark btn-sm">
      </div>  
    </form>`

  document.querySelector('#renew-form').addEventListener('submit', () => renew(id))
}


function renew(id){

  let csrftoken = getCookie('csrftoken');

  const date = document.querySelector('#valid-date').value

  fetch('/renew', {
    method: 'POST',
    body: JSON.stringify({
      id: id,
      date:date
    }),
    headers: { "X-CSRFToken": csrftoken },

  })
  window.location.reload(`${id}`);
}*/


function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}