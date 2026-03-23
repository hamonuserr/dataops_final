# ML Platform

## Реализовано:

- **API сервис** - FastAPI для прогнозов
- **MLflow** - Отслеживание экспериментов
- **Airflow** - Автоматизация рабочих процессов
- **LakeFS** - Управление данными
- **JupyterHub** - Среда разработки
- **Grafana** - Графики и мониторинг
- **PostgreSQL** - База данных
- **Kubernetes** - Развертывание

### Запуск
```bash
cd dataops_final
docker-compose up -d
```

### Проверка
```bash
# Проверить состояние
curl http://localhost:8000/health

# Сделать прогноз
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 45, "sex": 1, "bmi": 25.5, "bp": 120, "s1": 200, "s2": 130, "s3": 50, "s4": 4, "s5": 2.5, "s6": 100}'
```

## Веб-интерфейсы

| Сервис | Адрес | Логин | Пароль |
|--------|-------|-------|--------|
| MLflow | http://localhost:5000 | - | - |
| Airflow | http://localhost:8080 | admin | admin |
| JupyterHub | http://localhost:8001 | admin | admin |
| LakeFS | http://localhost:8000 | admin | admin123 |
| Prometheus | http://localhost:9090 | - | - |
| Grafana | http://localhost:3000 | admin | admin |

## Основные команды
# Посмотреть логи
docker-compose logs -f diabetes-service

# Остановить
docker-compose down


## API примеры
```bash
# Здоровье
curl http://localhost:8000/health

# Информация о модели
curl http://localhost:8000/api/v1/model-info

# Метрики
curl http://localhost:8000/metrics
```

## Развертывание на Kubernetes
```bash
# С манифестами
kubectl apply -f k8s-manifests/

# С Helm
helm install diabetes-service ./helm-diabetes-service -n ml-platform --create-namespace
```
