from pathlib import Path

scripts_dir = Path(r"D:\antigravityStudy\StarInvader\Assets\Scripts")
editor_dir = scripts_dir / "Editor"
scripts_dir.mkdir(parents=True, exist_ok=True)
editor_dir.mkdir(parents=True, exist_ok=True)

# 1. Update PlayerController.cs with Lives, Damage, and Invincibility
player_code = """using System;
using System.Collections;
using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 플레이어 조작, 발사, 체력(목숨) 및 피격/무적 제어 (player.py 대응)
    /// </summary>
    public class PlayerController : MonoBehaviour
    {
        [Header("이동 설정")]
        [SerializeField] private float moveSpeed = GameConstants.PLAYER_SPEED;
        [SerializeField] private float minX = -GameConstants.SCREEN_WIDTH_HALF;
        [SerializeField] private float maxX = GameConstants.SCREEN_WIDTH_HALF;

        [Header("발사 설정")]
        [SerializeField] private GameObject bulletPrefab;
        [SerializeField] private Transform firePoint;
        [SerializeField] private float shootCooldown = GameConstants.PLAYER_SHOOT_COOLDOWN;
        [SerializeField] private int maxConcurrentBullets = GameConstants.PLAYER_MAX_BULLETS;

        [Header("라이프 및 무적 설정")]
        [SerializeField] private int maxLives = GameConstants.PLAYER_MAX_LIVES;
        [SerializeField] private float invincibleDuration = GameConstants.PLAYER_INVINCIBLE_DURATION;

        private int currentLives;
        private bool isInvincible = false;
        private float lastShootTime = -10f;
        private SpriteRenderer spriteRenderer;

        public event Action<int> OnLivesChanged;
        public event Action OnPlayerDied;

        private void Awake()
        {
            currentLives = maxLives;
            spriteRenderer = GetComponent<SpriteRenderer>();
        }

        private void Start()
        {
            if (firePoint == null)
            {
                GameObject fp = new GameObject("FirePoint");
                fp.transform.SetParent(transform);
                fp.transform.localPosition = new Vector3(0, 0.5f, 0);
                firePoint = fp.transform;
            }

            OnLivesChanged?.Invoke(currentLives);
        }

        private void Update()
        {
            HandleMovement();
            HandleShooting();
        }

        private void HandleMovement()
        {
            float horizontalInput = Input.GetAxisRaw("Horizontal");
            Vector3 position = transform.position;
            position.x += horizontalInput * moveSpeed * Time.deltaTime;
            position.x = Mathf.Clamp(position.x, minX, maxX);
            transform.position = position;
        }

        private void HandleShooting()
        {
            if (Input.GetKey(KeyCode.Space) || Input.GetButton("Fire1"))
            {
                if (Time.time >= lastShootTime + shootCooldown)
                {
                    int activeBulletCount = 0;
                    Bullet[] existingBullets = FindObjectsByType<Bullet>(FindObjectsSortMode.None);
                    foreach (var b in existingBullets)
                    {
                        if (!b.IsEnemyBullet) activeBulletCount++;
                    }

                    if (activeBulletCount < maxConcurrentBullets)
                    {
                        Shoot();
                    }
                }
            }
        }

        private void Shoot()
        {
            lastShootTime = Time.time;

            if (bulletPrefab != null)
            {
                Instantiate(bulletPrefab, firePoint.position, Quaternion.identity);
            }
        }

        public void TakeDamage(int damage = 1)
        {
            if (isInvincible || currentLives <= 0) return;

            currentLives -= damage;
            OnLivesChanged?.Invoke(currentLives);

            Debug.Log($"[플레이어 피격] 남은 목숨: {currentLives}");

            if (currentLives <= 0)
            {
                Die();
            }
            else
            {
                StartCoroutine(InvincibilityRoutine());
            }
        }

        private IEnumerator InvincibilityRoutine()
        {
            isInvincible = true;
            float elapsed = 0f;
            float flashInterval = 0.1f;

            while (elapsed < invincibleDuration)
            {
                if (spriteRenderer != null)
                {
                    spriteRenderer.enabled = !spriteRenderer.enabled;
                }
                yield return new WaitForSeconds(flashInterval);
                elapsed += flashInterval;
            }

            if (spriteRenderer != null)
            {
                spriteRenderer.enabled = true;
            }
            isInvincible = false;
        }

        private void Die()
        {
            Debug.Log("[플레이어 사망] 게임 오버!");
            OnPlayerDied?.Invoke();
            gameObject.SetActive(false);
        }

        public int CurrentLives => currentLives;
        public bool IsInvincible => isInvincible;
    }
}
"""
(scripts_dir / "PlayerController.cs").write_text(player_code, encoding="utf-8")

# 2. Update Bullet.cs for both Player and Enemy Bullet Collision
bullet_code = """using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 플레이어 및 적 탄환 기본 동작 및 충돌 판정 (bullet.py 대응)
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
            if (!isEnemyBullet)
            {
                // [플레이어 탄환] -> 적 피격
                Enemy enemy = other.GetComponent<Enemy>();
                if (enemy != null)
                {
                    enemy.TakeDamage(damage);
                    Destroy(gameObject);
                }
            }
            else
            {
                // [적 탄환] -> 플레이어 피격
                PlayerController player = other.GetComponent<PlayerController>();
                if (player != null)
                {
                    player.TakeDamage(damage);
                    Destroy(gameObject);
                }
            }
        }

        public void SetSpeed(float newSpeed)
        {
            speed = newSpeed;
        }

        public void SetEnemyBullet(bool enemyBullet)
        {
            isEnemyBullet = enemyBullet;
        }

        public bool IsEnemyBullet => isEnemyBullet;
    }
}
"""
(scripts_dir / "Bullet.cs").write_text(bullet_code, encoding="utf-8")

# 3. Update EnemyFleet.cs with Attack Shooting and Invasion Limit Check
fleet_code = """using System.Collections.Generic;
using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 적 편대 이동, 속도 가속, 반격 사격 및 침략 한계선 관리 (enemy.py 대응)
    /// </summary>
    public class EnemyFleet : MonoBehaviour
    {
        [Header("프리팹 설정")]
        [SerializeField] private GameObject topEnemyPrefab;
        [SerializeField] private GameObject midEnemyPrefab;
        [SerializeField] private GameObject bottomEnemyPrefab;
        [SerializeField] private GameObject enemyBulletPrefab;

        [Header("이동 설정")]
        [SerializeField] private float baseSpeed = GameConstants.ENEMY_BASE_SPEED_X;
        [SerializeField] private float maxSpeed = 5.5f;
        [SerializeField] private float dropDistance = GameConstants.ENEMY_DROP_DISTANCE;
        [SerializeField] private float boundaryX = GameConstants.SCREEN_WIDTH_HALF - 0.3f;
        [SerializeField] private float invasionYLimit = GameConstants.INVASION_Y_LIMIT;

        [Header("사격 설정")]
        [SerializeField] private float shootIntervalMin = 0.8f;
        [SerializeField] private float shootIntervalMax = 2.0f;

        private List<Enemy> activeEnemies = new List<Enemy>();
        private int totalInitialEnemies = 0;
        private int moveDirection = 1; // 1: 우측, -1: 좌측
        private float currentSpeed;
        private float nextShootTime = 0f;

        private void Start()
        {
            SpawnFleet();
            ScheduleNextShot();
        }

        public void SpawnFleet()
        {
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

            // 1. 편대 이동
            float deltaX = moveDirection * currentSpeed * Time.deltaTime;
            bool hitBoundary = false;
            bool reachedInvasionLimit = false;

            foreach (var enemy in activeEnemies)
            {
                if (enemy == null) continue;
                Vector3 pos = enemy.transform.position;
                pos.x += deltaX;
                enemy.transform.position = pos;

                // 좌우 경계 도달 확인
                if (moveDirection > 0 && pos.x >= boundaryX) hitBoundary = true;
                else if (moveDirection < 0 && pos.x <= -boundaryX) hitBoundary = true;

                // 침략 한계선 도달 확인
                if (pos.y <= invasionYLimit) reachedInvasionLimit = true;
            }

            // 2. 방향 반전 및 하강
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

            // 3. 침략선 돌파 판정
            if (reachedInvasionLimit)
            {
                PlayerController player = FindAnyObjectByType<PlayerController>();
                if (player != null && player.gameObject.activeSelf)
                {
                    Debug.LogWarning("[외계인 침략 성공] 적이 방어선을 뚫었습니다!");
                    player.TakeDamage(999); // 즉시 패배 처리
                }
            }

            // 4. 적 반격 사격
            if (Time.time >= nextShootTime)
            {
                ShootRandomEnemyBullet();
                ScheduleNextShot();
            }
        }

        private void ShootRandomEnemyBullet()
        {
            List<Enemy> bottomEnemies = GetBottomEnemies();
            if (bottomEnemies.Count == 0) return;

            Enemy shooter = bottomEnemies[Random.Range(0, bottomEnemies.Count)];
            if (shooter != null && enemyBulletPrefab != null)
            {
                Vector3 spawnPos = shooter.transform.position + Vector3.down * 0.3f;
                Instantiate(enemyBulletPrefab, spawnPos, Quaternion.identity);
            }
        }

        private List<Enemy> GetBottomEnemies()
        {
            // 각 열에서 가장 아래쪽에 있는 적만 선별 (스페이스 인베이더 규칙)
            Dictionary<int, Enemy> columnBottomMap = new Dictionary<int, Enemy>();

            foreach (var enemy in activeEnemies)
            {
                if (enemy == null) continue;
                // X좌표를 반올림하여 열(Column) 식별
                int colKey = Mathf.RoundToInt(enemy.transform.position.x * 10f);

                if (!columnBottomMap.ContainsKey(colKey) || enemy.transform.position.y < columnBottomMap[colKey].transform.position.y)
                {
                    columnBottomMap[colKey] = enemy;
                }
            }

            return new List<Enemy>(columnBottomMap.Values);
        }

        private void ScheduleNextShot()
        {
            nextShootTime = Time.time + Random.Range(shootIntervalMin, shootIntervalMax);
        }

        private void HandleEnemyDestroyed(Enemy enemy)
        {
            activeEnemies.Remove(enemy);

            if (totalInitialEnemies > 0)
            {
                float destroyedRatio = 1f - ((float)activeEnemies.Count / totalInitialEnemies);
                currentSpeed = Mathf.Lerp(baseSpeed, maxSpeed, destroyedRatio);
            }

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

# 4. Update StarInvaderSetupTool.cs with Step 3 Menu
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
            SetupStep3SceneInternal(false);
            EditorUtility.DisplayDialog("Star Invader", "2단계 구성이 완료되었습니다!\\n\\n유니티 상단의 [▶ (Play)] 버튼을 눌러 테스트해 보세요.", "확인");
        }

        [MenuItem("Star Invader/3단계: 적 공격 및 플레이어 라이프 시스템 구성", false, 3)]
        public static void SetupStep3Scene()
        {
            SetupStep3SceneInternal(true);
            EditorUtility.DisplayDialog("Star Invader", "3단계 (적 탄환 반격, 플레이어 피격/목숨 감소, 무적 깜빡임, 침략 한계선) 구성이 완료되었습니다!\\n\\n유니티 상단의 [▶ (Play)] 버튼을 눌러 테스트해 보세요.", "확인");
        }

        private static void SetupStep3SceneInternal(bool includeEnemyBullets)
        {
            SetupCamera();
            GameObject bulletPrefabObj = SetupBulletPrefab();
            SetupPlayer(bulletPrefabObj);

            GameObject topEnemyPrefab = SetupEnemyPrefab("Enemy_Top", "Assets/GameAssets/images/enemy/enemy_top.png", EnemyType.Top, Color.magenta);
            GameObject midEnemyPrefab = SetupEnemyPrefab("Enemy_Mid", "Assets/GameAssets/images/enemy/enemy_mid.png", EnemyType.Mid, new Color(1f, 0.6f, 0.2f));
            GameObject bottomEnemyPrefab = SetupEnemyPrefab("Enemy_Bottom", "Assets/GameAssets/images/enemy/enemy_bottom.png", EnemyType.Bottom, Color.yellow);
            GameObject enemyBulletPrefab = SetupEnemyBulletPrefab();

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
            if (includeEnemyBullets)
            {
                serializedFleet.FindProperty("enemyBulletPrefab").objectReferenceValue = enemyBulletPrefab;
            }
            serializedFleet.ApplyModifiedProperties();

            Selection.activeGameObject = fleetObj;
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
                bSr.color = new Color(0.47f, 1.0f, 1.0f, 1.0f);
                
                Texture2D bulletTex = MakeColorTexture(16, 40, Color.cyan);
                Sprite bulletSprite = Sprite.Create(bulletTex, new Rect(0, 0, 16, 40), new Vector2(0.5f, 0.5f), 100f);
                bSr.sprite = bulletSprite;

                BoxCollider2D bc = tempBullet.AddComponent<BoxCollider2D>();
                bc.isTrigger = true;
                bc.size = new Vector2(0.16f, 0.4f);

                Bullet b = tempBullet.AddComponent<Bullet>();
                b.SetSpeed(GameConstants.PLAYER_BULLET_SPEED);
                b.SetEnemyBullet(false);

                bulletPrefabObj = PrefabUtility.SaveAsPrefabAsset(tempBullet, bulletPrefabPath);
                GameObject.DestroyImmediate(tempBullet);
            }
            return bulletPrefabObj;
        }

        private static GameObject SetupEnemyBulletPrefab()
        {
            string prefabsDir = "Assets/Prefabs";
            if (!AssetDatabase.IsValidFolder(prefabsDir))
            {
                AssetDatabase.CreateFolder("Assets", "Prefabs");
            }

            string bulletPrefabPath = "Assets/Prefabs/EnemyBullet.prefab";
            GameObject bulletPrefabObj = AssetDatabase.LoadAssetAtPath<GameObject>(bulletPrefabPath);
            if (bulletPrefabObj == null)
            {
                GameObject tempBullet = new GameObject("EnemyBullet");
                SpriteRenderer bSr = tempBullet.AddComponent<SpriteRenderer>();
                bSr.color = new Color(1.0f, 0.35f, 0.35f, 1.0f); // 핫 레드
                
                Texture2D bulletTex = MakeColorTexture(16, 40, Color.red);
                Sprite bulletSprite = Sprite.Create(bulletTex, new Rect(0, 0, 16, 40), new Vector2(0.5f, 0.5f), 100f);
                bSr.sprite = bulletSprite;

                BoxCollider2D bc = tempBullet.AddComponent<BoxCollider2D>();
                bc.isTrigger = true;
                bc.size = new Vector2(0.16f, 0.4f);

                Bullet b = tempBullet.AddComponent<Bullet>();
                b.SetSpeed(GameConstants.ENEMY_BULLET_SPEED);
                b.SetEnemyBullet(true);

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
            col.size = new Vector2(0.5f, 0.4f);

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
                col.size = new Vector2(0.4f, 0.32f);

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

print("Step 3 Unity scripts and Editor tool created successfully!")
