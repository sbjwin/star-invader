from pathlib import Path

scripts_dir = Path(r"D:\antigravityStudy\StarInvader\Assets\Scripts")
editor_dir = scripts_dir / "Editor"
scripts_dir.mkdir(parents=True, exist_ok=True)
editor_dir.mkdir(parents=True, exist_ok=True)

# 1. Update GameConstants.cs with Enemy Fleet Settings
constants_code = """using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 게임 전반에서 사용되는 상수 및 기본 밸런스 값 정의 (constants.py 대응)
    /// </summary>
    public static class GameConstants
    {
        // 화면 경계 (카메라 Orthographic Size 5 기준, 종횡비 3:4 / 9:16)
        public const float SCREEN_WIDTH_HALF = 3.5f;   // X축 좌우 이동 한계 (-3.5 ~ 3.5)
        public const float SCREEN_HEIGHT_HALF = 5.0f;  // Y축 상하 경계 (-5.0 ~ 5.0)

        // 플레이어 설정
        public const float PLAYER_SPEED = 8.0f;
        public const float PLAYER_START_Y = -4.0f;
        public const float PLAYER_SHOOT_COOLDOWN = 0.22f; // 발사 쿨다운(초)
        public const int PLAYER_MAX_BULLETS = 3;          // 화면 동시 탄환 수
        public const int PLAYER_MAX_LIVES = 3;
        public const float PLAYER_INVINCIBLE_DURATION = 1.2f;

        // 탄환 설정
        public const float PLAYER_BULLET_SPEED = 14.0f;
        public const float ENEMY_BULLET_SPEED = 6.0f;

        // 적 편대 (Alien Fleet) 설정
        public const int ENEMY_ROWS = 3;                  // 편대 행 수
        public const int ENEMY_COLS = 8;                  // 편대 열 수 (총 24기)
        public const float ENEMY_SPACING_X = 0.75f;       // 가로 간격
        public const float ENEMY_SPACING_Y = 0.65f;       // 세로 간격
        public const float ENEMY_START_Y = 3.5f;          // 편대 시작 Y 위치
        public const float ENEMY_BASE_SPEED_X = 1.8f;     // 기본 이동 속도
        public const float ENEMY_DROP_DISTANCE = 0.35f;   // 벽 충돌 시 하강 거리
        public const int SCORE_PER_ENEMY = 100;           // 적 격파 기본 점수
        public const float INVASION_Y_LIMIT = -3.2f;      // 침략 한계선
    }
}
"""
(scripts_dir / "GameConstants.cs").write_text(constants_code, encoding="utf-8")

# 2. Enemy.cs
enemy_code = """using System;
using UnityEngine;

namespace StarInvader
{
    public enum EnemyType
    {
        Top,    // 상단 (핑크)
        Mid,    // 중단 (주황)
        Bottom  // 하단 (노랑)
    }

    /// <summary>
    /// 개별 적 기체 컴포넌트 (enemy.py 대응)
    /// </summary>
    public class Enemy : MonoBehaviour
    {
        [Header("적 속성")]
        [SerializeField] private EnemyType enemyType = EnemyType.Bottom;
        [SerializeField] private int scoreValue = GameConstants.SCORE_PER_ENEMY;
        [SerializeField] private int maxHp = 1;

        private int currentHp;
        public event Action<Enemy> OnDestroyed;

        private void Awake()
        {
            currentHp = maxHp;
        }

        public void Setup(EnemyType type, int score = GameConstants.SCORE_PER_ENEMY)
        {
            enemyType = type;
            scoreValue = score;
        }

        public void TakeDamage(int damage = 1)
        {
            currentHp -= damage;
            if (currentHp <= 0)
            {
                Die();
            }
        }

        private void Die()
        {
            OnDestroyed?.Invoke(this);
            // 향후 폭발 이펙트/사운드 재생 추가 예정
            Destroy(gameObject);
        }

        public EnemyType Type => enemyType;
        public int ScoreValue => scoreValue;
    }
}
"""
(scripts_dir / "Enemy.cs").write_text(enemy_code, encoding="utf-8")

# 3. EnemyFleet.cs
fleet_code = """using System.Collections.Generic;
using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 적 편대 전체의 이동, 하강 및 가속 관리 (enemy.py의 편대 로직 대응)
    /// </summary>
    public class EnemyFleet : MonoBehaviour
    {
        [Header("프리팹 설정")]
        [SerializeField] private GameObject topEnemyPrefab;
        [SerializeField] private GameObject midEnemyPrefab;
        [SerializeField] private GameObject bottomEnemyPrefab;

        [Header("이동 설정")]
        [SerializeField] private float baseSpeed = GameConstants.ENEMY_BASE_SPEED_X;
        [SerializeField] private float maxSpeed = 5.5f;
        [SerializeField] private float dropDistance = GameConstants.ENEMY_DROP_DISTANCE;
        [SerializeField] private float boundaryX = GameConstants.SCREEN_WIDTH_HALF - 0.3f;

        private List<Enemy> activeEnemies = new List<Enemy>();
        private int totalInitialEnemies = 0;
        private int moveDirection = 1; // 1: 우측, -1: 좌측
        private float currentSpeed;

        private void Start()
        {
            SpawnFleet();
        }

        public void SpawnFleet()
        {
            // 기존 적이 남아있다면 제거
            ClearFleet();

            int rows = GameConstants.ENEMY_ROWS;
            int cols = GameConstants.ENEMY_COLS;
            float spacingX = GameConstants.ENEMY_SPACING_X;
            float spacingY = GameConstants.ENEMY_SPACING_Y;
            float startY = GameConstants.ENEMY_START_Y;

            float totalWidth = (cols - 1) * spacingX;
            float startX = -totalWidth / 2f;

            for (int r = 0; r < rows; r++)
            {
                EnemyType rowType = (r == 0) ? EnemyType.Top : (r == 1 ? EnemyType.Mid : EnemyType.Bottom);
                GameObject prefab = GetPrefabForType(rowType);

                for (int c = 0; c < cols; c++)
                {
                    Vector3 spawnPos = new Vector3(startX + (c * spacingX), startY - (r * spacingY), 0);
                    GameObject enemyObj = null;

                    if (prefab != null)
                    {
                        enemyObj = Instantiate(prefab, spawnPos, Quaternion.identity, transform);
                    }
                    else
                    {
                        // 임시 적 기체 생성
                        enemyObj = CreateFallbackEnemy(rowType, spawnPos);
                    }

                    Enemy enemyComp = enemyObj.GetComponent<Enemy>();
                    if (enemyComp == null) enemyComp = enemyObj.AddComponent<Enemy>();
                    enemyComp.Setup(rowType);
                    enemyComp.OnDestroyed += HandleEnemyDestroyed;

                    activeEnemies.Add(enemyComp);
                }
            }

            totalInitialEnemies = activeEnemies.Count;
            currentSpeed = baseSpeed;
            moveDirection = 1;
        }

        private void Update()
        {
            if (activeEnemies.Count == 0) return;

            // 1. 편대 좌우 이동
            float deltaX = moveDirection * currentSpeed * Time.deltaTime;
            bool hitBoundary = false;

            foreach (var enemy in activeEnemies)
            {
                if (enemy == null) continue;
                Vector3 pos = enemy.transform.position;
                pos.x += deltaX;
                enemy.transform.position = pos;

                // 화면 경계 충돌 체크
                if (moveDirection > 0 && pos.x >= boundaryX)
                {
                    hitBoundary = true;
                }
                else if (moveDirection < 0 && pos.x <= -boundaryX)
                {
                    hitBoundary = true;
                }
            }

            // 2. 경계 도달 시 방향 반전 및 전체 하강
            if (hitBoundary)
            {
                moveDirection *= -1;
                foreach (var enemy in activeEnemies)
                {
                    if (enemy == null) continue;
                    Vector3 pos = enemy.transform.position;
                    pos.y -= dropDistance;
                    enemy.transform.position = pos;
                }
            }
        }

        private void HandleEnemyDestroyed(Enemy enemy)
        {
            activeEnemies.Remove(enemy);

            // 적이 줄어들수록 이동 속도 점진적 가속 (클래식 인베이더 기믹)
            if (totalInitialEnemies > 0)
            {
                float destroyedRatio = 1f - ((float)activeEnemies.Count / totalInitialEnemies);
                currentSpeed = Mathf.Lerp(baseSpeed, maxSpeed, destroyedRatio);
            }

            // 모든 적 처치 시 웨이브 재스폰
            if (activeEnemies.Count == 0)
            {
                Invoke(nameof(SpawnFleet), 1.0f);
            }
        }

        private GameObject GetPrefabForType(EnemyType type)
        {
            switch (type)
            {
                case EnemyType.Top: return topEnemyPrefab;
                case EnemyType.Mid: return midEnemyPrefab;
                case EnemyType.Bottom: return bottomEnemyPrefab;
                default: return bottomEnemyPrefab;
            }
        }

        private GameObject CreateFallbackEnemy(EnemyType type, Vector3 pos)
        {
            GameObject obj = new GameObject($"Enemy_{type}");
            obj.transform.position = pos;
            obj.transform.SetParent(transform);

            SpriteRenderer sr = obj.AddComponent<SpriteRenderer>();
            sr.color = type == EnemyType.Top ? Color.magenta : (type == EnemyType.Mid ? new Color(1f, 0.5f, 0.2f) : Color.yellow);

            BoxCollider2D col = obj.AddComponent<BoxCollider2D>();
            col.isTrigger = true;

            return obj;
        }

        public void ClearFleet()
        {
            foreach (var enemy in activeEnemies)
            {
                if (enemy != null) Destroy(enemy.gameObject);
            }
            activeEnemies.Clear();
        }
    }
}
"""
(scripts_dir / "EnemyFleet.cs").write_text(fleet_code, encoding="utf-8")

# 4. Update Bullet.cs with Collision Check
bullet_code = """using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 플레이어 및 적 탄환 기본 동작 및 충돌 스크립트 (bullet.py 대응)
    /// </summary>
    public class Bullet : MonoBehaviour
    {
        [Header("탄환 속성")]
        [SerializeField] private bool isEnemyBullet = false;
        [SerializeField] private float speed = GameConstants.PLAYER_BULLET_SPEED;
        [SerializeField] private int damage = 1;

        private void Update()
        {
            // 이동 방향 (플레이어: 위쪽 +Y, 적: 아래쪽 -Y)
            Vector3 direction = isEnemyBullet ? Vector3.down : Vector3.up;
            transform.position += direction * (speed * Time.deltaTime);

            // 화면 밖으로 나가면 파괴
            if (transform.position.y > GameConstants.SCREEN_HEIGHT_HALF + 1.0f ||
                transform.position.y < -GameConstants.SCREEN_HEIGHT_HALF - 1.0f)
            {
                Destroy(gameObject);
            }
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            // 플레이어 탄환이 적과 충돌했을 때
            if (!isEnemyBullet)
            {
                Enemy enemy = other.GetComponent<Enemy>();
                if (enemy != null)
                {
                    enemy.TakeDamage(damage);
                    Destroy(gameObject); // 탄환 소멸
                }
            }
        }

        public void SetSpeed(float newSpeed)
        {
            speed = newSpeed;
        }

        public bool IsEnemyBullet => isEnemyBullet;
    }
}
"""
(scripts_dir / "Bullet.cs").write_text(bullet_code, encoding="utf-8")

# 5. Update StarInvaderSetupTool.cs with Step 2 Menu
editor_setup_code = """using UnityEngine;
using UnityEditor;
using System.IO;

namespace StarInvader.Editor
{
    public class StarInvaderSetupTool : EditorWindow
    {
        [MenuItem("Star Invader/1단계: 플레이어 및 씬 자동 구성", false, 1)]
        public static void SetupStep1Scene()
        {
            SetupCamera();
            GameObject bulletPrefabObj = SetupBulletPrefab();
            SetupPlayer(bulletPrefabObj);

            EditorUtility.DisplayDialog("Star Invader", "1단계 (카메라, 플레이어, 탄환) 구성이 완료되었습니다!\\n\\n유니티 상단의 [▶ (Play)] 버튼을 눌러 테스트해 보세요.", "확인");
        }

        [MenuItem("Star Invader/2단계: 적 편대 및 충돌 시스템 구성", false, 2)]
        public static void SetupStep2Scene()
        {
            // 1단계 요소 먼저 확인/구성
            SetupCamera();
            GameObject bulletPrefabObj = SetupBulletPrefab();
            SetupPlayer(bulletPrefabObj);

            // 2단계 적 프리팹 및 EnemyFleet 구성
            GameObject topEnemyPrefab = SetupEnemyPrefab("Enemy_Top", "Assets/GameAssets/images/enemy/enemy_top.png", EnemyType.Top, Color.magenta);
            GameObject midEnemyPrefab = SetupEnemyPrefab("Enemy_Mid", "Assets/GameAssets/images/enemy/enemy_mid.png", EnemyType.Mid, new Color(1f, 0.6f, 0.2f));
            GameObject bottomEnemyPrefab = SetupEnemyPrefab("Enemy_Bottom", "Assets/GameAssets/images/enemy/enemy_bottom.png", EnemyType.Bottom, Color.yellow);

            // EnemyFleet 오브젝트 씬에 배치
            GameObject fleetObj = GameObject.Find("EnemyFleet");
            if (fleetObj == null)
            {
                fleetObj = new GameObject("EnemyFleet");
            }

            EnemyFleet fleet = fleetObj.GetComponent<EnemyFleet>();
            if (fleet == null) fleet = fleetObj.AddComponent<EnemyFleet>();

            SerializedObject serializedFleet = new SerializedObject(fleet);
            serializedFleet.FindProperty("topEnemyPrefab").objectReferenceValue = topEnemyPrefab;
            serializedFleet.FindProperty("midEnemyPrefab").objectReferenceValue = midEnemyPrefab;
            serializedFleet.FindProperty("bottomEnemyPrefab").objectReferenceValue = bottomEnemyPrefab;
            serializedFleet.ApplyModifiedProperties();

            Selection.activeGameObject = fleetObj;
            EditorUtility.DisplayDialog("Star Invader", "2단계 (적 편대 24기 스폰, 좌우 이동/하강 및 탄환 충돌 피격) 구성이 완료되었습니다!\\n\\n유니티 상단의 [▶ (Play)] 버튼을 눌러 테스트해 보세요.", "확인");
        }

        private static void SetupCamera()
        {
            Camera mainCam = Camera.main;
            if (mainCam == null)
            {
                GameObject camObj = new GameObject("Main Camera");
                mainCam = camObj.AddComponent<Camera>();
                camObj.tag = "MainCamera";
            }

            mainCam.orthographic = true;
            mainCam.orthographicSize = 5f;
            mainCam.transform.position = new Vector3(0, 0, -10f);
            mainCam.backgroundColor = new Color(0.04f, 0.04f, 0.08f, 1f);
            mainCam.clearFlags = CameraClearFlags.SolidColor;
        }

        private static GameObject SetupBulletPrefab()
        {
            string prefabsDir = "Assets/Prefabs";
            if (!AssetDatabase.IsValidFolder(prefabsDir))
            {
                AssetDatabase.CreateFolder("Assets", "Prefabs");
            }

            string bulletPrefabPath = "Assets/Prefabs/PlayerBullet.prefab";
            GameObject bulletPrefabObj = AssetDatabase.LoadAssetAtPath<GameObject>(bulletPrefabPath);
            if (bulletPrefabObj == null)
            {
                GameObject tempBullet = new GameObject("PlayerBullet");
                SpriteRenderer bSr = tempBullet.AddComponent<SpriteRenderer>();
                bSr.color = new Color(0.47f, 1.0f, 1.0f, 1.0f); // 네온 시안
                
                Texture2D bulletTex = MakeColorTexture(16, 40, Color.cyan);
                Sprite bulletSprite = Sprite.Create(bulletTex, new Rect(0, 0, 16, 40), new Vector2(0.5f, 0.5f), 100f);
                bSr.sprite = bulletSprite;

                BoxCollider2D bc = tempBullet.AddComponent<BoxCollider2D>();
                bc.isTrigger = true;
                bc.size = new Vector2(0.16f, 0.4f);

                tempBullet.AddComponent<Bullet>();

                bulletPrefabObj = PrefabUtility.SaveAsPrefabAsset(tempBullet, bulletPrefabPath);
                GameObject.DestroyImmediate(tempBullet);
            }
            return bulletPrefabObj;
        }

        private static void SetupPlayer(GameObject bulletPrefabObj)
        {
            GameObject playerObj = GameObject.Find("Player");
            if (playerObj == null)
            {
                playerObj = new GameObject("Player");
            }

            playerObj.transform.position = new Vector3(0, GameConstants.PLAYER_START_Y, 0);
            SpriteRenderer sr = playerObj.GetComponent<SpriteRenderer>();
            if (sr == null) sr = playerObj.AddComponent<SpriteRenderer>();

            string playerSpritePath = "Assets/GameAssets/images/player/player.png";
            EnsureSpriteImport(playerSpritePath);
            Sprite playerSprite = AssetDatabase.LoadAssetAtPath<Sprite>(playerSpritePath);
            if (playerSprite != null) sr.sprite = playerSprite;

            BoxCollider2D col = playerObj.GetComponent<BoxCollider2D>();
            if (col == null) col = playerObj.AddComponent<BoxCollider2D>();
            col.isTrigger = true;

            PlayerController controller = playerObj.GetComponent<PlayerController>();
            if (controller == null) controller = playerObj.AddComponent<PlayerController>();

            SerializedObject serializedPlayer = new SerializedObject(controller);
            SerializedProperty bulletProp = serializedPlayer.FindProperty("bulletPrefab");
            if (bulletProp != null && bulletPrefabObj != null)
            {
                bulletProp.objectReferenceValue = bulletPrefabObj;
                serializedPlayer.ApplyModifiedProperties();
            }
        }

        private static GameObject SetupEnemyPrefab(string name, string spritePath, EnemyType type, Color fallbackColor)
        {
            string prefabsDir = "Assets/Prefabs";
            if (!AssetDatabase.IsValidFolder(prefabsDir))
            {
                AssetDatabase.CreateFolder("Assets", "Prefabs");
            }

            string prefabPath = $"Assets/Prefabs/{name}.prefab";
            GameObject prefabObj = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            if (prefabObj == null)
            {
                GameObject tempEnemy = new GameObject(name);
                SpriteRenderer sr = tempEnemy.AddComponent<SpriteRenderer>();

                EnsureSpriteImport(spritePath);
                Sprite enemySprite = AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
                if (enemySprite != null)
                {
                    sr.sprite = enemySprite;
                }
                else
                {
                    sr.color = fallbackColor;
                    Texture2D tex = MakeColorTexture(32, 32, fallbackColor);
                    sr.sprite = Sprite.Create(tex, new Rect(0, 0, 32, 32), new Vector2(0.5f, 0.5f), 100f);
                }

                BoxCollider2D col = tempEnemy.AddComponent<BoxCollider2D>();
                col.isTrigger = true;

                Enemy enemy = tempEnemy.AddComponent<Enemy>();
                enemy.Setup(type);

                prefabObj = PrefabUtility.SaveAsPrefabAsset(tempEnemy, prefabPath);
                GameObject.DestroyImmediate(tempEnemy);
            }
            return prefabObj;
        }

        private static void EnsureSpriteImport(string path)
        {
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer != null && importer.textureType != TextureImporterType.Sprite)
            {
                importer.textureType = TextureImporterType.Sprite;
                importer.SaveAndReimport();
            }
        }

        private static Texture2D MakeColorTexture(int width, int height, Color col)
        {
            Texture2D tex = new Texture2D(width, height);
            Color[] pix = new Color[width * height];
            for (int i = 0; i < pix.Length; i++) pix[i] = col;
            tex.SetPixels(pix);
            tex.Apply();
            return tex;
        }
    }
}
"""
(editor_dir / "StarInvaderSetupTool.cs").write_text(editor_setup_code, encoding="utf-8")

print("Step 2 Unity scripts and Editor tool created successfully!")
