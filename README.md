# Order System Architecture Overview

## 🧱 系統軟體層級架構圖（Software Architecture Overview）
```
                  🌐 使用者 (Browser / Mobile App)
                               │
                               ▼
                  ┌──────────────────────────┐
                  │  Frontend (React GUI)     │
                  │  - 登入畫面               │
                  │  - 訂單 / 商品管理頁面     │
                  │  - 呼叫 REST API           │
                  └──────────┬────────────────┘
                             │ HTTPS (OIDC Token)
                             ▼
       ┌──────────────────────────────────────────┐
       │     3scale API Gateway (APIcast)         │
       │  - 驗證 OIDC Token (Keycloak)            │
       │  - 控制流量、金鑰、統計、API Plan         │
       └──────────┬───────────────────────────────┘
                  │ Authz OK → Forward Request
                  ▼
       ┌──────────────────────────────────────────┐
       │          Backend API (FastAPI)           │
       │  - 驗證 JWT / 業務邏輯 / 資料處理        │
       │  - 提供 /api/users /api/orders /api/products │
       └──────────┬───────────────────────────────┘
                  │ SQL Query
                  ▼
       ┌──────────────────────────────────────────┐
       │          PostgreSQL Database             │
       │  - 儲存 user / product / order 資料      │
       └──────────────────────────────────────────┘

                 🔒 OIDC Login / JWT
                 ┌──────────────────────────┐
                 │  Keycloak (SSO Provider) │
                 │  - 使用者登入 / Token發行  │
                 │  - 提供 Public Key (JWKS) │
                 └──────────────────────────┘
```

---

## 🧩 部署後容器間的實際溝通流程（Runtime Communication）

| 步驟 | 通訊方向                                      | 協定                 | 功能說明                         |
| -- | ----------------------------------------- | ------------------ | ---------------------------- |
| ①  | **Browser → Frontend (React)**            | HTTPS              | 使用者開啟系統 GUI（由 Route 提供）      |
| ②  | **Frontend → Keycloak**                   | HTTPS (OIDC)       | 使用者登入並取得 JWT Access Token    |
| ③  | **Frontend → APIcast (3scale Gateway)**   | HTTPS (REST + JWT) | 每次呼叫 API 時夾帶 Token           |
| ④  | **APIcast → Keycloak**                    | HTTPS (JWKS)       | 3scale 驗證 JWT 是否有效（簽章 / 有效期） |
| ⑤  | **APIcast → Backend (FastAPI)**           | HTTPS / HTTP       | 通過驗證後轉發 API 請求給後端服務          |
| ⑥  | **Backend → PostgreSQL**                  | TCP (5432)         | 後端執行查詢 / 寫入訂單資料              |
| ⑦  | **Backend → APIcast Response → Frontend** | HTTPS              | 回傳訂單 / 錯誤 / 成功結果             |
| ⑧  | **Frontend 顯示畫面給使用者**                     | —                  | 完成一次交易流程                     |

---

## ⚙️ OpenShift 容器部署對應

| Namespace          | 容器 / Pod                            | 功能                 |
| ------------------ | ----------------------------------- | ------------------ |
| `enterprise-infra` | 🗄️ PostgreSQL Pod                  | 訂單與商品資料儲存          |
| `enterprise-infra` | 🔐 Keycloak Pod                     | 身分登入與 OIDC Token   |
| `enterprise-app`   | ⚙️ Backend Pod (FastAPI)            | API 服務邏輯           |
| `enterprise-app`   | 🖥️ Frontend Pod (React build 靜態頁)  | GUI 界面             |
| `3scale-system`    | 🚪 3scale System / Zync / Backend   | 管理 API 結構與設定       |
| `3scale-gateway`   | 🧩 APIcast Gateway (Staging / Prod) | 驗證 Token、代理請求、統計流量 |

---

## 🔄 一句話描述整體情境

> 使用者在前端登入後，經由 **Keycloak 取得身份憑證（OIDC Token）**，所有 API 請求都透過 **3scale Gateway 驗證與控管**，最終由 **Backend API 實作業務邏輯並與 PostgreSQL 溝通**，形成一個可控流量、可追蹤、具身份驗證的企業級訂單系統。
