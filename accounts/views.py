from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('story_list')  # Redirect to the story list page after successful login
        else:
            # If authentication fails, you can return an error message
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')

def logout_view(request):
    if request.method == 'POST':
        # Handle logout logic here
        logout(request)
    elif request.method == 'GET':
        return render(request, 'accounts/logout.html')  # Render a logout confirmation page for GET requests
        
    return redirect('story_list')  # Redirect to the story list page if not a POST request