## Docker Instruction
1. docker compose up -d: -d表示后台运行，可以继续在terminal里输入其他命令
2. docker compose up -d --build: --build表示重建image，代码有改动就需要重新build
3. docker compose ps: 查看容器运行状态
4. docker compose logs backend -f: 查看容器内的日志打印，因为在容器内运行，日志不会直接打印在控制台上，需要到容器里查看
5. docker exec -it container_name bash: 进入（数据库）服务容器
6. 进入数据库容器后，运行psql -U username -d db_name，即可进入数据库
7. 在数据库中，db_name=#，运行\dt，可以查看已建立的表
8. \q退出数据库
9. 在容器中，执行ctrl+d或者exit即可退出容器
10. docker compose down: 停止容器