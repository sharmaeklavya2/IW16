<h1>API documentation for IW16</h1>
<p>For some of these requests, authentication is required. Authentication will be done using <code>sessionid</code> cookie.</p>
<p>All responses will be in <code>text/plain</code> or <code>application/json</code>. If a request fails, a <code>text/plain</code> response will be given with appropriate status code.</p>
<p>Datetimes will be in <a href="http://www.ecma-international.org/ecma-262/5.1/#sec-15.9.1.15">ECMA-262</a> format.</p>
<p>Common status codes:</p>
<table>
	<tr><td>Auth failure</td><td>401</td></tr>
	<tr><td>Form validation fails</td><td>400</td></tr>
	<tr><td>Invalid URL</td><td>404</td></tr>
	<tr><td>Not having game permissions or being a non-playing user</td><td>403</td></tr>
</table>
<ul>
	<li>
		<h2>GET /api/qno-list/</h2>
		<table>
			<tr><td>Request Format</td><td>-</td></tr>
			<tr><td>Response Format</td><td>application/json</td></tr>
			<tr><td>Login required</td><td>No</td></tr>
			<tr><td>Required game permission</td><td>view_ques</td></tr>
		</table>
		<h4>Response:</h4>
		<p>Returns a JSON list of valid question numbers.</p>
	</li>

	<li>
		<h2>GET /api/game-info/</h2>
		<table>
			<tr><td>Request Format</td><td>-</td></tr>
			<tr><td>Response Format</td><td>application/json</td></tr>
			<tr><td>Login required</td><td>No</td></tr>
		</table>
		<h4>Response:</h4>
		<p>Returns a JSON object with the following fields:</p>
		<table>
			<tr><td>total_questions</td><td>integer</td><td>Number of questions in the game</td></tr>
			<tr><td>max_score</td><td>integer</td><td>Sum of scores of all questions in the game</td></tr>
			<tr><td>base_datetime</td><td>datetime (string)</td><td>Datetime used to calculate total time of a user</td></tr>
			<tr><td>time_penalty_s</td><td>integer</td><td>Time penalty (in seconds) for wrong answer</td></tr>
			<tr>
				<td>perms</td><td>object</td>
				<td>Permissions for the game. The keys are permission names and values are booleans.</td>
			</tr>
		</table>
	</li>

	<li>
		<h2>GET /api/user-info/</h2>
		<table>
			<tr><td>Request Format</td><td>-</td></tr>
			<tr><td>Response Format</td><td>application/json</td></tr>
			<tr><td>Login required</td><td>Yes</td></tr>
		</table>
		<h4>Response:</h4>
		<p>Returns a JSON object with the following fields:</p>
		<table>
			<tr><td>username</td><td>string</td><td>Username of the logged in user</td></tr>
			<tr><td>score</td><td>integer</td><td>Sum of scores of all questions solved by the user</td></tr>
			<tr><td>time_taken_s</td><td>float</td><td>Sum of time taken (in seconds) by user for each correctly answered question</td></tr>
			<tr>
				<td>corrects</td><td>array of objects</td>
				<td>
					List of all questions correctly solved by user. Each question is a JSON object with the following fields:
					<table>
						<tr><td>qno</td><td>integer</td><td>Question number</td></tr>
						<tr><td>text</td><td>string</td><td>Answer given by the user</td></tr>
						<tr><td>attempts</td><td>integer</td><td>Number of attempts by the user, including the attempt which resulted in correct answer.</td></tr>
						<tr><td>time_taken_s</td><td>float</td><td>Time taken (in seconds) by user to solve this question. This includes the time penalty for incorrect submissions.</td></tr>
						<tr><td>time</td><td>datetime (string)</td><td>Time when user solved this question. This does not include time penalty.</td></tr>
					</table>
				</td>
			</tr>
			<tr>
				<td>wrongs</td><td>array of objects</td>
				<td>List of all questions wrongly attempted by user. Each question is a JSON object with the same fields as objects of 'corrects'.</td>
			</tr>
		</table>
	</li>

	<li>
		<h2>POST /api/login/</h2>
		<table>
			<tr><td>Request Format</td><td>application/x-www-form-urlencoded</td></tr>
			<tr><td>Response Format</td><td>text/plain</td></tr>
			<tr><td>Login required</td><td>No</td></tr>
		</table>
		<h4>Request:</h4>
		<ul>
			<li>username</li>
			<li>password</li>
		</ul>
		<h4>Response:</h4>
		<p>These are the possible responses:</p>
		<table>
			<tr><td>success</td><td>login was successful. <code>sessionid</code> cookie is set.</td></tr>
			<tr><td>inactive</td><td>The user's account is inactive. The user is not allowed to login.</td></tr>
			<tr><td>wrong_login</td><td>Credentials were incorrect.</td></tr>
		</table>
	</li>

	<li>
		<h2>POST /api/logout/</h2>
		<table>
			<tr><td>Request Format</td><td>-</td></tr>
			<tr><td>Response Format</td><td>text/plain</td></tr>
			<tr><td>Login required</td><td>No</td></tr>
		</table>
		<h4>Response:</h4>
		<p>Responds with 'logged out'.</p>
		<p>Deletes the session cookie from the database.</p>
	</li>

	<li>
		<h2>POST /api/submit/{qno}/</h2>
		<table>
			<tr><td>Request Format</td><td>application/x-www-form-urlencoded</td></tr>
			<tr><td>Response Format</td><td>application/json</td></tr>
			<tr><td>Login required</td><td>Yes</td></tr>
			<tr><td>Required game permission</td><td>answer</td></tr>
		</table>
		<h4>Request:</h4>
		<p>There should be a key named "answer" with a non-empty value.</p>
		<h4>Response:</h4>
		<p>Returns a JSON object with the following fields:</p>
		<table>
			<tr>
				<td>attstat</td><td>string</td>
				<td>Attempt Status: It can have 3 possible values - <code>correct</code>, <code>wrong</code> and <code>na</code>. <code>na</code> means this question is already solved. <code>time</code> and <code>time_taken_s</code> are <code>null</code> when <code>attstat</code> is <code>na</code>.</td></tr>
				</td>
			</tr>
			<tr><td>time_taken_s</td><td>float</td><td>Time taken (in seconds) by user to solve this question. This includes the time penalty for incorrect submissions.</td></tr>
			<tr><td>time</td><td>datetime (string)</td><td>Time when user solved this question. This does not include time penalty.</table>
		<p>If <code>qno</code> is invalid, 404 occurs.</p>
	</li>

	<li>
		<h2>GET /api/ldrbrd/</h2>
		<p>Gets a paginated leaderboard along with some other data.</p>
		<table>
			<tr><td>Request Format</td><td>An optional querystring</td></tr>
			<tr><td>Response Format</td><td>application/json</td></tr>
			<tr><td>Login required</td><td>Optional</td></tr>
			<tr><td>Required game permission</td><td>view_ldrbrd</td></tr>
		</table>
		<h4>Querystring:</h4>
		<p>page - Page number of the leaderboard page which is to be shown. Numbering starts from 1.</p>
		<h4>Response:</h4>
		<p>Returns a JSON object with the following fields:</p>
		<table>
			<tr><td>pages</td><td>integer</td><td>Number of pages in the leaderboard</td></tr>
			<tr><td>ldrbrd</td><td>list of lists</td>
			<td>A list made of lists of 3 elements - username, score, total time taken (in seconds)</td></tr>
			<tr><td>my_rank</td><td>integer</td><td>Rank of the user. This field is available only if the user is logged in.</td></tr>
			<tr><td>my_page</td><td>integer</td><td>Page where the user belongs to on the leaderboard. This field is available only if the user is logged in.</td></tr>
		</table>
		<h4>Example:</h4>
<pre><code>{
"ldrbrd": [
["user3", 3, -22319.183956],
["user1", 2, -15035.257432],
["user4", 2, -5872.349751]
],
"pages": 1
}
</code></pre>
	</li>

	<li>
		<h2>POST /api/register/</h2>
		<table>
			<tr><td>Request Format</td><td>application/x-www-form-urlencoded</td></tr>
			<tr><td>Response Format</td><td>text/plain</td></tr>
			<tr><td>Login required</td><td>No</td></tr>
			<tr><td>Required game permission</td><td>register</td></tr>
		</table>
		<h4>Request:</h4>
		<table>
            <tr><td>username *</td><td>sting</td></tr>
            <tr><td>password *</td><td>string</td></tr>
            <tr><td>name *</td><td>string</td></tr>
            <tr><td>email *</td><td>email</td></tr>
		</table>
		<h4>Response:</h4>
		<p>Returns text which could be one of the following:</p>
		<table>
			<tr><td>reg_closed</td><td>403</td><td>Registration is closed</td></tr>
			<tr><td>invalid_data</td><td>400</td><td>Form did not pass django's validation</td></tr>
			<tr><td>username_taken</td><td>200</td><td>This username is already in use by someone else</td></tr>
		</table>
	</li>

	<li>
		<h2>GET /api/hint-status/{qno}/</h2>
		<table>
			<tr><td>Request Format</td><td>-</td></tr>
			<tr><td>Response Format</td><td>application/json</td></tr>
			<tr><td>Login required</td><td>Optional</td></tr>
			<tr><td>Required game permission</td><td>-</td></tr>
		</table>
		<h4>Response:</h4>
		<p>Returns a JSON object with the following fields:</p>
		<table>
			<tr><td>take_hint_perm</td><td>boolean</td><td>Whether take_hint game permission is on</td></tr>
			<tr><td>hint_enabled</td><td>boolean</td><td>whether hint is enabled for this question</td></tr>
			<tr><td>hint_penalty</td><td>integer</td><td>Penalty for taking this hint. This field is visible only if take_hint_perm and hint_enabled are trur.</td></tr>
			<tr><td>hint_taken</td><td>boolean</td><td>Whether user has taken hint for this question. This field is available only if the user is logged in.</td></tr>
		</table>
	</li>

	<li>
		<h2>POST /api/take-hint/{qno}/</h2>
		<table>
			<tr><td>Request Format</td><td>-</td></tr>
			<tr><td>Response Format</td><td>text/plain</td></tr>
			<tr><td>Login required</td><td>Yes</td></tr>
			<tr><td>Required game permission</td><td>take_hint</td></tr>
		</table>
		<h4>Response:</h4>
		<p>Returns the hint as the text. If the hint cannot be viewed, status code 403 is raised.</p>
	</li>
</ul>
