<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8">
    <title><?php echo htmlspecialchars( $page_title ); ?> - 用户列表</title>
  </head>
  <body>
    <h1>用户管理</h1>
    <?php if($is_admin): ?>
      <div class="admin-panel">
        <p>欢迎管理员！</p>
        <a href="/admin">进入管理后台</a>
      </div>
    <?php else: ?>
      <div class="user-panel">
        <p>普通用户</p>
      </div>
      <ul class="user-list">
        <?php foreach($users as $user): ?>
          <li>
            <strong><?php echo htmlspecialchars( $user.name ); ?></strong>
            <span>(@<?php echo htmlspecialchars( $user.email ); ?>)</span>
          </li>
        <?php endforeach; ?>
      </ul>
      <footer>
        <p>&copy; <?php echo htmlspecialchars( $year ); ?> MyApp</p>
      </footer>
      <script>
      function greet() {
              alert('Hello from LiteML!');
            }
      </script>
    <?php endif; ?>
  </body>
</html>