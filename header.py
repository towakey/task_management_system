def header():
    print("""
<html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>TaskManagementSystem</title>
        <link rel="stylesheet" href="./css/bootstrap.css">
        <script src="./js/bootstrap.bundle.js"></script>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
            <div class="container-fluid">
                <a class="navbar-brand" href="./index.py">TaskManagementSystem</a>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a class="nav-link" href="./index.py?mode=create">新規作成</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
""")
