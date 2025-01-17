{% extends "base.html" %}
{% block content %}
    <h2>Login</h2>
    <form method="POST" action="/login">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required><br><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required><br><br>
        <button class="btn" type="submit">Login</button>
    </form>
{% endblock %}
