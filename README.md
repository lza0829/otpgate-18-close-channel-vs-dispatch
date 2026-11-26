# 验码渠（Otpgate）

骨架：通道注册 → 选路投递 → 失败熔断切备通道 → 送达回执对账

- 前端 http://127.0.0.1:6900
- API http://127.0.0.1:11900
- 数据库环境变量 `OTPGATE_DB`（容器内默认 `/data/otpgate.db`）

```bash
docker compose up -d --build
```
