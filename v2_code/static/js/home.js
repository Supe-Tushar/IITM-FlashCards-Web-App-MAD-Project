
const Login = Vue.component('login', {
    template: `
<div>
	<h1>Login</h1>
	<form v-on:submit.prevent="loginSubmitForm" method="post">
		<div class="container">
			<div class="form-group">
				<label for="uemail"><b>User Email: </b></label>
				<p style="font-size:12px;">(User email should be of format: '<--->@<--->.<--->')</p>
				<br/>
				<input type="text" class="form-control" placeholder="Enter Email Address" name="uemail" v-model="form.uemail" required>
			</div>
			<br/>
			<div class="form-group">
				<label for="password1"><b>Password: </b></label>
				<p style="font-size:12px;">(Password must contain only lower case letters and digits and should be 4 to 10 characters long.)</p>
				<br/>
				<input class="form-control" type="password" placeholder="Enter Password" name="password"  v-model="form.password" required>
			</div>
			<br/>
			<br/>
			<button type="submit" class="submit_button">Login</button>
			<br/>
			<router-link to="/signup" tag="button" class="cancelbtn">Sign Up</router-link>
		</div>
	</form>
</div>`,
	data: function() {
        return{
            form: {
                uemail: '',
				password:''
				
            }
        }
    },
	methods: {
        loginSubmitForm: async function() {
            fetch(this.$parent.baseurl+'/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    },
                    body: JSON.stringify(this.form),
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success login :', this.form, data);
					if (data.category == "success"){
						this.$parent.displayStatusSuccess(data.message);
						localStorage.setItem("userid", data.userid);
                        localStorage.setItem("token", data.token);
						this.$parent.userId = data.userid;
						this.loggedIn();}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}   
                })
                .catch((error) => {
                    console.error('Error:', error);  
                });
        },
		loggedIn: function (){
			this.$router.push("/dashboard");
			//this.$parent.displayStatusSuccess("Logged In");
		}
    }
})

const SignUp = Vue.component('signup', {
    template: `
<div>
	<h1>Sign Up</h1>
	<form v-on:submit.prevent="signUpSubmitForm" method="post">
		<div class="container">
			<div class="form-group">
				<label for="uname"><b>Username: </b></label>
				<p style="font-size:12px;">(Username must contain only lower case letters and digits and should be 4 to 10 characters long.)</p>
				
				<input type="text" class="form-control" placeholder="Enter Username" name="uname" v-model="form.uname" required>
			</div>
			<br/>
			<div class="form-group">
				<label for="uemail"><b>User Email: </b></label>
				<p style="font-size:12px;">(User email should be of format: '<--->@<--->.<--->')</p>
				
				<input type="text" class="form-control" placeholder="Enter Email Address" name="uemail" v-model="form.uemail" required>
			</div>
			<br/>
			<div class="form-group">
				<label for="password1"><b>Password: </b></label>
				<p style="font-size:12px;">(Password must contain only lower case letters and digits and should be 4 to 10 characters long.)</p>
				
				<input class="form-control" type="password" placeholder="Enter Password" name="password1"  v-model="form.password1" required>
				<br/>
				<label for="password2"><b>Repeat Password: </b></label>
				<br/>
				<input class="form-control" type="password" placeholder="Enter Password" name="password2"  v-model="form.password2" required>
			</div>
			<br/>
			<br/>
			<button type="submit" class="submit_button">Sign Up</button>
			<br/>
			<router-link to="/login" tag="button" class="cancelbtn">Cancel</router-link>
		</div>
	</form>
</div>`,
	data: function() {
        return{
            form: {
                uname: '',
                uemail: '',
				password1:'',
				password2:''
            }
        }
    },
	methods: {
        signUpSubmitForm: async function() {
            fetch(this.$parent.baseurl+'/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    },
                    body: JSON.stringify(this.form),
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){
						this.$parent.displayStatusSuccess(data.message);
						localStorage.setItem("userid", data.userid);
						this.$parent.userId = data.userid;
						this.loggedIn();
						}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}   
                })
                .catch((error) => {
                    console.error('Error:', error);  
                });
        },
		loggedIn: function (){
			this.$router.push("/login");
			this.$parent.displayStatusSuccess("Log in now");
		}
    }
})

const Logout = Vue.component('logout', {
    template: '',
    mounted: function (){
        localStorage.setItem('token', '');
        this.$router.push("/login");
        this.$parent.displayStatusSuccess("Logged out successfully");
    }
});

const Dashboard = Vue.component('dashboard', {
    template: `
<div>
	<h1>Dashboard</h1>
	<p>Last reviewed deck name: {{ last_rev_deck_name }}</p>
	<div class="tableBlock">
		<table id="all_decks" class="table">
			<tr>
				<th style="width: 60px;">Srno</th>
				<th>Deck Name</th>
				<th>Description</th>
				<th style="width: 200px;">Last Reviewed Time</th>
				<th style="width: 60px;">Last Reviewed Score</th>
				<th style="width: 60px;">Overall Score</th>
				<th style="width: 60px;">Review</th>
				<th style="width: 60px;">Edit</th>
				<th style="width: 60px;">Delete</th>
				<th style="width: 60px;">Export</th>
			</tr>

                
			<tr v-for="(deck, index) in decks">
				<td>{{index + 1}}</td>
				<td>{{deck.deckname}}</td>
				<td>{{deck.deckdesc}}</td>
				<td>{{deck.ltime}}</td>
				<td>{{deck.lscore}}</td>
				<td>{{deck.oscore}}</td>
				<td><router-link :to="'/deck/'+deck.deckid+'/review'" tag="button">Review</router-link></td>
				<td><router-link :to="'/deck/'+deck.deckid+'/edit'" tag="button">Edit</router-link></td>
				<td><button v-on:click="deleteDeck(deck.deckid); return false;">Delete</button></td>
				<td><button v-on:click="exportDeck(deck.deckid); return false;">Export</button></td>
			</tr>
		</table>
	</div>

	<div class="import_deck">
		<br/>
		<router-link to="/deck/add" tag="button" class="button" id="addDeck">Add a deck (Manually)</router-link><br/>
		<router-link to="/deck/import" tag="button" class="button" id="importDeck">Import a deck (From CSV file)</router-link>
		</br>
		<button v-on:click="generateReport(); return false;">Generate Report (for demo)</button>
		<button v-on:click="sendAlert(); return false;">Send Alert (for demo)</button>
	</div>
</div>`,
	data: function() {
        return {
            decks: [],
			last_rev_deck_name: ""
        }
    },
    methods: {
		deleteDeck: async function(did) {
			console.log("delete deck click ", did);
			
			fetch(this.$parent.baseurl+'/api/deck/'+did, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    },
					credentials: "same-origin"
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);} 
					this.decks = this.decks.filter(function(deck, index, arr){ return deck.deckid != did;});
                })
                .catch((error) => {
                    console.error('Error:', error);           
                }); 
		},
		exportDeck: async function(did) {
			console.log("export deck click ", did);
			
			fetch(this.$parent.baseurl+'/deck/'+did+'/export', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){
						this.$parent.displayStatusSuccess(data.message);
						this.$parent.check_job_status(data.job_id);
						}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);} 
					
                })
                .catch((error) => {
                    console.error('Error:', error);           
                }); 
		},
		generateReport: async function() {
			console.log("generateReport click ");
			
			fetch(this.$parent.baseurl+'/generate_report', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){
						this.$parent.displayStatusSuccess(data.message);
						this.$parent.check_job_status(data.job_id);
						}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);} 
					
                })
                .catch((error) => {
                    console.error('Error:', error);           
                }); 
		},
		sendAlert: async function() {
			console.log("send alert click ");
			
			fetch(this.$parent.baseurl+'/send_alert', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){
						this.$parent.displayStatusSuccess(data.message);
						//this.$parent.check_job_status(data.job_id);
						}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);} 
					
                })
                .catch((error) => {
                    console.error('Error:', error);           
                }); 
		}
    },
    computed: {
    },
    mounted: async function() {
        console.log("dashboard mount token: ", JSON.stringify({'token':localStorage.getItem('token')}));
		fetch(this.$parent.baseurl+'/api/deck', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
                    // if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					// if (data.category == "error"){this.$parent.displayStatusError(data.message);} 

					let deckidList = data.deckidList ? data.deckidList : [];
					let alldecks = [];
					
					var max_time = 0;
					var last_rev_name = "";
					if (deckidList.length > 0 ) {
						for (let deckid of deckidList){
						
						fetch(this.$parent.baseurl+`/api/deck/${deckid}`, {
								method: 'GET',
								headers: {
									'Content-Type': 'application/json',
                                    'token': localStorage.getItem('token')
								}
							})
							.then(response => response.json())
							.then(data => {
								console.log('Success ltime:', data.ltime);
								let date = new Date(data.ltime*1000); // second to millisecond for javascript
								let formatdate = date.getDate()+"/"+(date.getMonth()+1)+"/"+date.getFullYear()+" "+date.getHours()+":"+date.getMinutes()+":"+date.getSeconds();
								if (data.ltime != null){
									if (data.ltime >= max_time){
										max_time = data.ltime;
										last_rev_name = data.deckname;
									}
									data.ltime = formatdate;
								}
								alldecks.push(data);
								this.last_rev_deck_name = last_rev_name;
								
							})
							.catch((error) => {
								console.error('Error:', error);
								
							}); 		
						}
					}
					this.decks = alldecks;
                })
                .catch((error) => {
                    console.error('Error:', error);
                    
                });  
    }
})

const DeckAdd = Vue.component('deckadd', {
    template: `
<div>
	<h1>Add a deck</h1>
	<form v-on:submit.prevent="deckAddSubmitForm" method="post">
		<div class="container">
			<div class="form-group">
				<label for="deckname"><b>Deck Name:</b></label>
				<p style="font-size:12px;">(Deck name must be unique and can't be edited later.)</p>
				<br/>
				<input type="text" class="form-control" placeholder="Enter deck name" name="deckname" v-model="form.deckname" required>
			</div>
			<br/>
			<div class="form-group">
				<label for="deckdesc"><b>Deck Description:</b></label>
				<br/>
				<input type="text" class="form-control" placeholder="Enter deck description" name="deckdesc" v-model="form.deckdesc" required>

			</div>
			<br/>
			<br/>
			<button type="submit" class="submit_button">Add Deck</button>
			<br/>
			<router-link to="/dashboard" tag="button" class="cancelbtn">Cancel</router-link>
		</div>
	</form>
</div>`,
	data: function() {
        return{
            form: {
                deckname: '',
                deckdesc: ''
            }
        }
    },
	methods: {
        deckAddSubmitForm: async function() {
            fetch(this.$parent.baseurl+'/api/deck', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    },
                    body: JSON.stringify(this.form),
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }
    }
})

const DeckEdit = Vue.component('deckedit', {
    template: `
<div>
	<h1>Edit Deck</h1>
	<router-link :to="'/deck/'+deckid+'/edit_desc'" tag="button" class="button">Edit Deck Description</router-link><br/>
	<div class="tableBlock">
        <table id = "all_decks" class="table">
                <tr>
                    <th style="width: 60px;">Srno</th>
                    <th>Question</th>
                    <th>Answer</th>
                    <th style="width: 200px;">Last Reviewed Time</th>
                    <th style="width: 60px;">Last Reviewed Score</th>
                    <th style="width: 60px;">Edit</th>
                    <th style="width: 60px;">Delete</th>
                </tr>

                <tr v-for="(card, index) in cards">
                    <td>{{ index + 1 }}</td>
                    <td>{{ card.question }}</td>
                    <td>{{ card.answer }}</td>
                    <td>{{ card.ltime }}</td>
                    <td>{{ card.lscore }}</td>
					<td><router-link :to="'/deck/'+deckid+'/card/'+card.cardid+'/edit'" tag="button">Edit</router-link></td>
					<td><button v-on:click="deleteCard(deckid, card.cardid); return false;">Delete</button></td>
                </tr>
		</table>
    </div>
    <div class="addcard">
        <br /><router-link :to="'/deck/'+deckid+'/card/add'" tag="button" class="button" id="addCard">Add a card to this deck</router-link><br/>
    </div>
</div>`,
	data: function() {
        return {
            cards: [],
			deckid: localStorage.getItem("deckid")
        }
    },
    methods: {
		deleteCard: async function(did, cid) {
			console.log("vonclick", did, cid);

			fetch(this.$parent.baseurl+'/api/deck/'+this.deckid+'/card/'+cid, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}
					this.cards = this.cards.filter(function(card, index, arr){ return card.cardid != cid;});
                })
                .catch((error) => {
                    console.error('Error:', error);

                });
		}

    },
    computed: {

    },
	beforeCreate: function() {
		let curr_deck = this.$route.params.deckid;
		localStorage.setItem("deckid", curr_deck);
		//console.log("before create ", localStorage.getItem("deckid"));
	},

    mounted: async function() {
		//console.log("in mounted ", localStorage.getItem("deckid"));

		fetch(this.$parent.baseurl+'/api/deck/'+this.deckid, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}

					let allcards = [];
					for (let card of data.cards){
						let date = new Date(card.ltime*1000); // second to millisecond for javascript
						let formatdate = date.getDate()+"/"+(date.getMonth()+1)+"/"+date.getFullYear()+" "+date.getHours()+":"+date.getMinutes()+":"+date.getSeconds();
						if (card.ltime != null){
							card.ltime = formatdate;
						}
						allcards.push(card);
					}
					this.cards = allcards;
                })
                .catch((error) => {
                    console.error('Error:', error);

                });
    }
})

const DeckEditDesc = Vue.component('deckeditdesc', {
    template: `
<div>
	<h1>Edit Deck Description</h1>
	<form v-on:submit.prevent="deckEditDescSubmitForm" method="post">
		<div class="container">
			<div class="form-group">
				<label for="deckname"><b>Deck Name:</b></label>
				<p style="font-size:12px;">(can not be edited)</p>
				<input type="text" class="form-control" placeholder="Enter deck name" name="deckname"  v-model="form.deckname" disabled>
			</div>
			<br/>
			<div class="form-group">
				<label for="deckdesc"><b>Deck Description: </b></label>
				<br/>
				<input type="text" class="form-control" placeholder="Enter deck description" name="deckdesc"  v-model="form.deckdesc" required>
			</div>
			<br/>
			<br/>
			<button type="submit" class="submit_button">Update Deck Description</button>
			<br/>
			<router-link :to="'/deck/'+deckid+'/edit'" tag="button" class="cancelbtn">Cancel</router-link>
		</div>
	</form>
</div>`,
	data: function() {
        return{
            form: {
                deckname: '',
                deckdesc: ''
            },
			deckid: localStorage.getItem("deckid")
        }
    },
	beforeCreate: function() {
		let curr_deck = this.$route.params.deckid;
		localStorage.setItem("deckid", curr_deck);
	},
	methods: {
        deckEditDescSubmitForm: async function() {
			console.log("Deck desc edit: ",JSON.stringify(this.form));
            fetch(this.$parent.baseurl+'/api/deck/'+this.deckid, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    },
                    body: JSON.stringify(this.form),
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }
    },
	created: async function() {
		await fetch(this.$parent.baseurl+'/api/deck/'+this.deckid, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}
					this.form.deckname = data.deckname;
					this.form.deckdesc = data.deckdesc;
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
	}
})

const CardEdit = Vue.component('cardedit', {
    template: `
<div>
	<h1>Edit Card</h1>
	<form v-on:submit.prevent="cardEditSubmitForm" method="post">
		<div class="container">
			<div class="form-group">
				<label for="question"><b>Question: </b></label>
				<p style="font-size:12px;">(Question must be unique.)</p>
				<input type="text" class="form-control" placeholder="Enter question text" name="question"  v-model="form.question" required>
			</div>
			<br/>
			<div class="form-group">
				<label for="answer"><b>Answer: </b></label>
				<br/>
				<input type="text" class="form-control" placeholder="Enter answer text" name="answer"  v-model="form.answer" required>
			</div>
			<br/>
			<br/>
			<button type="submit" class="submit_button">Update card</button>
			<br/>
			<router-link :to="'/deck/'+deckid+'/edit'" tag="button" class="cancelbtn">Cancel</router-link>
		</div>
	</form>
</div>`,
	data: function() {
        return{
            form: {
                question: '',
                answer: ''
            },
			deckid: localStorage.getItem("deckid"),
			cardid: localStorage.getItem("cardid")
        }
    },
	beforeCreate: function() {
		let curr_deck = this.$route.params.deckid;
		let curr_card = this.$route.params.cardid;
		localStorage.setItem("deckid", curr_deck);
		localStorage.setItem("cardid", curr_card);
	},
	methods: {
        cardEditSubmitForm: async function() {
            fetch(this.$parent.baseurl+'/api/deck/'+this.deckid+'/card/'+this.cardid, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    },
                    body: JSON.stringify(this.form),
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }
    },
	created: async function() {
		await fetch(this.$parent.baseurl+'/api/deck/'+this.deckid+'/card/'+this.cardid, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}
					this.form.question = data.question;
					this.form.answer = data.answer;

                })
                .catch((error) => {
                    console.error('Error:', error);

                });

	}
})

const CardAdd = Vue.component('cardadd', {
    template: `
<div>
	<h1>Add Card</h1>
	<form v-on:submit.prevent="cardAddSubmitForm" method="post">
		<div class="container">
			<div class="form-group">
				<label for="question"><b>Question: </b></label>
				<p style="font-size:12px;">(Question must be unique.)</p>
				<br/>
				<input type="text" class="form-control" placeholder="Enter question text" name="question"  v-model="form.question" required>
			</div>
			<br/>
			<div class="form-group">
				<label for="answer"><b>Answer: </b></label>
				<br/>
				<input type="text" class="form-control" placeholder="Enter answer text" name="answer"  v-model="form.answer" required>
			</div>
			<br/>
			<br/>
			<button type="submit" class="submit_button">Add card</button>
			<br/>
			<router-link :to="'/deck/'+deckid+'/edit'" tag="button" class="cancelbtn">Cancel</router-link>
		</div>
	</form>
</div>`,
	data: function() {
        return{
            form: {
                question: '',
                answer: ''
            },
			deckid: localStorage.getItem("deckid")
        }
    },
	beforeCreate: function() {
		let curr_deck = this.$route.params.deckid;
		localStorage.setItem("deckid", curr_deck);
	},
	methods: {
        cardAddSubmitForm: async function() {
            fetch(this.$parent.baseurl+'/api/deck/'+this.deckid+'/card', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    },
                    body: JSON.stringify(this.form),
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }
    }
})

const DeckReview = Vue.component('deckreview', {
    template: `
<div class='container2'>
	<div class='card_word' >
		<p class="word" id="word"><b>{{ form.question }}</b></p>
		<p class="answer" id="answer">
			<b>{{ form.question }}</b>
			<br />
			<br />
			{{ form.answer }}
		</p>
	</div>
	<div class='flipcard' >
		<button class='navitem' id='flip' type="button" v-on:click="flipcard">Flip</button>
	</div>
	<form v-on:submit.prevent="cardReviewSubmitForm" method="POST" id="create-form">
		<div class='difficulty'>
			<label>Select Difficulty of this card: </label>
			<br />
			<br />
			<input type="radio" id='radio_easy' name="choice" value="5" v-model="form.easy" required />
			<label>Easy</label>
			<br />
			<input type="radio" id='radio_medium' name="choice" value="3" v-model="form.easy" required/>
			<label>Medium</label>
			<br />
			<input type="radio" id='radio_hard' name="choice" value="0" v-model="form.easy" required/>
			<label>Difficult</label>
			<br />
		</div>
		<br />
		<div class='nav_buttons'>
			<input class='navitem' id='next' type="submit" value="Next" >
		</div>
	</form>   
</div>`,
	data: function() {
        return {
            cards: [],
			form: {
                question: '',
                answer: '',
				easy:''
            },
			deckid: localStorage.getItem("deckid"),
			cardid: localStorage.getItem("cardid"),
			current_score: 0,
			cards_reviewed:0,
			reviewcards:[],
			curr_review_card:null,
			oscore:0.0,
			flip:true // show answer when true
        }
    },
    methods: {
		flipcard: function() {
			console.log("flip card clicked");
			let x = document.getElementById("word"); // question
			let y = document.getElementById("answer"); // question and answer
			if (this.flip){
				console.log("in flip if", this.flip );
				x.style.display = "none"; //hide question
				y.style.display = "block"; // show question and answer
				this.flip = false;
			}
			else{
				console.log("in flip else", this.flip );
				y.style.display = "none";
				x.style.display = "block";
				this.flip = true;
			}

		},
		cardReviewSubmitForm: async function() {
			console.log(JSON.stringify(this.form));
			console.log(localStorage.getItem("cardid"));
			console.log(localStorage.getItem("shuffledCards"));
			console.log(localStorage.getItem("current_score"));
			console.log(localStorage.getItem("cards_reviewed"));
			this.cardid = localStorage.getItem("cardid");

			//update card score in db
            fetch(this.$parent.baseurl+'/api/deck/'+this.deckid+'/card/'+this.cardid, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    },
                    body: JSON.stringify({'ltime':parseInt(Date.now()/1000) , 'lscore':parseInt(this.form.easy)}),
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}
                })
                .catch((error) => {
                    console.error('Error:', error);
                });

			// cache score
			this.current_score = this.current_score + parseInt(this.form.easy);
			this.cards_reviewed = this.cards_reviewed + 1;
			localStorage.setItem("current_score", this.current_score);
			localStorage.setItem("cards_reviewed", this.cards_reviewed);
			console.log(localStorage.getItem("current_score"));
			console.log(localStorage.getItem("cards_reviewed"));

			// load next card
			this.reviewcards = JSON.parse(localStorage.getItem("shuffledCards"));
            if (this.reviewcards.length <= 0){
				this.$parent.displayStatusSuccess("All cards reviewed");
				if (this.cards_reviewed != 0){
					this.oscore = this.current_score/this.cards_reviewed;
					this.oscore = parseFloat(this.oscore.toFixed(1));
				}else{
					this.oscore = 0.0;
				}
				fetch(this.$parent.baseurl+'/api/deck/'+this.deckid, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    },
                    body: JSON.stringify({'ltime':parseInt(Date.now()/1000) , 'lscore':this.oscore}),
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}
                })
                .catch((error) => {
                    console.error('Error:', error);
                });

				this.$router.push("/dashboard");
			}else{

				this.curr_review_card = this.reviewcards.shift();
				this.flip = false;
				this.flipcard();
				this.form.question = this.curr_review_card.question;
				this.form.answer = this.curr_review_card.answer;
				this.form.easy = '';
				this.$parent.displayStatusSuccess("Next card loaded");
				localStorage.setItem("cardid", this.curr_review_card.cardid);
				localStorage.setItem("shuffledCards", JSON.stringify(this.reviewcards));

			}
        }

    },
    computed: {

    },
	beforeCreate: function() {
		let curr_deck = this.$route.params.deckid;
		localStorage.setItem("deckid", curr_deck);
	},
	created: async function() {
		await fetch(this.$parent.baseurl+'/api/deck/'+this.deckid, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'token': localStorage.getItem('token')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}
					this.reviewcards = data.cards;
					if (this.reviewcards.length <= 0){
						this.$parent.displayStatusError("This deck does not have any cards");
						this.$router.push("/dashboard");
					}
					else{
					// shuffle array of cards
						if (this.reviewcards.length > 2){
							for (let i = this.reviewcards.length - 1; i > 0; i--) {
							// Generate random number
							let j = Math.floor(Math.random() * (i + 1));
							let temp = this.reviewcards[i];
							this.reviewcards[i] = this.reviewcards[j];
							this.reviewcards[j] = temp;
							}
						}
					console.log("before shift length ",this.reviewcards.length);
					console.log("before shift ",this.reviewcards);
					this.curr_review_card = this.reviewcards.shift();
					console.log("current review card ",this.curr_review_card);

					this.form.question = this.curr_review_card.question;
					this.form.answer = this.curr_review_card.answer;



					console.log("remaining cards ",JSON.stringify(this.reviewcards));

					localStorage.setItem("cardid", this.curr_review_card.cardid);
					localStorage.setItem("shuffledCards", JSON.stringify(this.reviewcards));
					localStorage.setItem("current_score", this.current_score);
					localStorage.setItem("cards_reviewed", this.cards_reviewed);
				}
                })
                .catch((error) => {
                    console.error('Error:', error);

                });

	}
})

const DeckImport = Vue.component('deckimport', {
    template: `
<div>
	<h1>Import a deck from CSV file</h1>
	<form action="/deck/import" method="post" enctype = "multipart/form-data">
		<div class="container">
			<div class="form-group">
				<label for="deckname"><b>Deck Name: </b></label>
				<p style="font-size:12px;">(Deck name must be unique and can't be edited later.)</p>
				<br/>
				<input type="text" class="form-control" placeholder="Enter deck name" name="deckname" required>
			</div>
			<br/>
			<div class="form-group">
				<label for="deckdesc"><b>Deck Description:</b></label>
				<br/>
				<input type="text" class="form-control" placeholder="Enter deck description" name="deckdesc" required>
			</div>
			<br/>
			<div class='importfile'>
                <label for="uploadfile"><b>Select a CSV file to import:</b></label>
                <input type="file" id="uploadfile" name="file" required>
                <p>(Note: CSV file must have header ['Srno', 'Question', 'Answer']) </p>
                <br />
		    </div>
			<br/>
			<!--<button type="button" class="submit_button" v-on:click="redirectF"></button>-->
			<button type="submit" class="submit_button">Import Deck</button>
			<br/>
			<router-link to="/dashboard" tag="button" class="cancelbtn">Cancel</router-link>
		</div>
	</form>
</div>`,
	data: function() {
        return{
            form: {
                deckname: '',
                deckdesc: '',
				file: ''
            },

        }
    },
	methods: {
		
		uploadFile: function() {
        this.form.file = this.$refs.file.files[0];
		console.log("file changed", this.form.file);
		console.log("deck data ", this.form.deckname, this.form.deckdesc);
      },
        deckImportSubmitForm: async function() {
			var formData = new FormData();
			formData.append('file', this.form.file);
			formData.append('deckname', this.form.deckname);
			formData.append('deckdesc', this.form.deckdesc);
			this.$parent.redirectF();
            fetch(this.$parent.baseurl+'/deck/import', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'multipart/form-data' ,
                        'token': localStorage.getItem('token')
                    },
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					
					if (data.category == "success"){this.$parent.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.$parent.displayStatusError(data.message);}
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }
    }
})


// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

const routes = [ 
{
    path: '/login',
    component: Login
},{
    path: '/signup',
    component: SignUp
},{
    path: '/logout',
    component: Logout
},{
    path: '/dashboard',
    component: Dashboard
},{
    path: '/deck/add',
    component: DeckAdd
},{
    path: '/deck/import',
    component: DeckImport
},{
    path: '/deck/:deckid/edit',
    component: DeckEdit
},{
    path: '/deck/:deckid/edit_desc',
    component: DeckEditDesc
},{
    path: '/deck/:deckid/review',
    component: DeckReview
},{
    path: '/deck/:deckid/card/:cardid/edit',
    component: CardEdit
},{
    path: '/deck/:deckid/card/add',
    component: CardAdd
}];

const router = new VueRouter({
	mode: 'history',
  hash: false,
  routes: routes
})

var app = new Vue({
    el: '#app_1',
    router: router,
    data: {
		baseurl: "http://127.0.0.1:5000",
		userId: null
    },
    methods: {
		displayStatusSuccess: function(msg){
			document.getElementById("alertSuccess").innerText = msg;
			document.getElementById("success").style.display = "block";
			setTimeout(() => {
                        document.getElementById("alertSuccess").innerText = "";
					   document.getElementById("success").style.display = "none";
                    }, 3000);
		},
		displayStatusError: function(msg){
			document.getElementById("alertError").innerText = msg;
			document.getElementById("error").style.display = "block";
			setTimeout(() => {
                        document.getElementById("alertError").innerText = "";
					   document.getElementById("error").style.display = "none";
                    }, 3000);
		},
		check_job_status: async function(job_id){
			setTimeout(() => {
			fetch(this.baseurl+'/job_status', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json' ,
                        'token': localStorage.getItem('token'),
						'job_id':job_id
                    }
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
					if (data.category == "success"){this.displayStatusSuccess(data.message);}
					if (data.category == "error"){this.displayStatusError(data.message);}
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
				}, 5000);
			
		},
		redirectF: function(){
			setTimeout(() => {this.$router.push("/dashboard");}, 3000);
		},
    },
	mounted: function(){
		document.getElementById("success").style.display = "none";
		document.getElementById("error").style.display = "none";
	}
})