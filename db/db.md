# DB 초기 구축

## docker-compose.yaml 파일 작성

`docker-compose.yaml` 파일 참고

## 초기 테이블 구축 (예정)

컨테이너 접속: `docker compose exec mariadb bash`

MariaDB 접속: `mariadb -u root -p` 명령어 실행 후 root 계정 비밀번호 입력.

사용할 데이터베이스 선택: `USE btc;`

테이블 생성

```sql
CREATE TABLE IF NOT EXISTS btc_15m (
  ts        DATETIME NOT NULL,
  open      DOUBLE   NOT NULL,
  high      DOUBLE   NOT NULL,
  low       DOUBLE   NOT NULL,
  close     DOUBLE   NOT NULL,
  volume    DOUBLE   NOT NULL,
  rsi       DOUBLE   NOT NULL,
  -- bb        DOUBLE,
  PRIMARY KEY (ts)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

잘 생성됐는지 못 믿겠으면 `SHOW TABLES;` 및 `DESCRIBE btc_15m;` 명령어 실행.

각 시간대별 테이블 생성(btc_1h, btc_4h 등)