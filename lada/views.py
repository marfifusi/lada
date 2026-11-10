from django.shortcuts import render


# Mostra la descrizione del progetto
def index(request):
    context = {}
    return render(request, 'index.html', context=context)


# Mostra la pagina per chi pubblica i dati di ricerca
def data_contributor(request):
    context = {}
    return render(request, 'data_contributor.html', context=context)