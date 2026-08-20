from pathlib import Path

scripts_dir = Path(r"D:\antigravityStudy\StarInvader\Assets\Scripts")
editor_dir = scripts_dir / "Editor"
scripts_dir.mkdir(parents=True, exist_ok=True)
editor_dir.mkdir(parents=True, exist_ok=True)

# 1. GameConstants.cs
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
    }
}
"""
(scripts_dir / "GameConstants.cs").write_text(constants_code, encoding="utf-8")

# 2. Bullet.cs
bullet_code = """using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 플레이어 및 적 탄환 기본 동작 스크립트 (bullet.py 대응)
    /// </summary>
    public class Bullet : MonoBehaviour
    {
        [Header("탄환 속성")]
        [SerializeField] private bool isEnemyBullet = false;
        [SerializeField] private float speed = GameConstants.PLAYER_BULLET_SPEED;

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

        public void SetSpeed(float newSpeed)
        {
            speed = newSpeed;
        }

        public bool IsEnemyBullet => isEnemyBullet;
    }
}
"""
(scripts_dir / "Bullet.cs").write_text(bullet_code, encoding="utf-8")

# 3. PlayerController.cs
player_code = """using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 플레이어 이동 및 기본 사격 컨트롤러 (player.py 대응)
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

        private float lastShootTime = -10f;

        private void Start()
        {
            // 발사 위치가 지정되지 않았으면 플레이어 위치 기준으로 자동 생성
            if (firePoint == null)
            {
                GameObject fp = new GameObject("FirePoint");
                fp.transform.SetParent(transform);
                fp.transform.localPosition = new Vector3(0, 0.5f, 0);
                firePoint = fp.transform;
            }
        }

        private void Update()
        {
            HandleMovement();
            HandleShooting();
        }

        private void HandleMovement()
        {
            float horizontalInput = Input.GetAxisRaw("Horizontal"); // A/D 또는 좌우 화살표
            Vector3 position = transform.position;
            position.x += horizontalInput * moveSpeed * Time.deltaTime;

            // 좌우 이동 범위 제한 (Clamp)
            position.x = Mathf.Clamp(position.x, minX, maxX);
            transform.position = position;
        }

        private void HandleShooting()
        {
            // 스페이스바 또는 기본 사격 키 입력 확인
            if (Input.GetKey(KeyCode.Space) || Input.GetButton("Fire1"))
            {
                if (Time.time >= lastShootTime + shootCooldown)
                {
                    // 현재 활성화된 플레이어 탄환 수 확인
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
            else
            {
                // 프리팹이 없을 경우 기본 Quad로 임시 발사
                GameObject defaultBullet = GameObject.CreatePrimitive(PrimitiveType.Quad);
                defaultBullet.name = "PlayerBullet";
                defaultBullet.transform.position = firePoint.position;
                defaultBullet.transform.localScale = new Vector3(0.15f, 0.4f, 1f);
                
                Collider col = defaultBullet.GetComponent<Collider>();
                if (col != null) Destroy(col);

                defaultBullet.AddComponent<BoxCollider2D>();
                defaultBullet.AddComponent<Bullet>();
            }
        }
    }
}
"""
(scripts_dir / "PlayerController.cs").write_text(player_code, encoding="utf-8")

# 4. Editor Setup Tool: StarInvaderSetupTool.cs
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
            // 1. 카메라 세팅
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

            // 2. 탄환 프리팹 생성 (Prefabs 폴더)
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
                tempBullet.AddComponent<Bullet>();

                bulletPrefabObj = PrefabUtility.SaveAsPrefabAsset(tempBullet, bulletPrefabPath);
                GameObject.DestroyImmediate(tempBullet);
            }

            // 3. 플레이어 오브젝트 생성 또는 갱신
            GameObject playerObj = GameObject.Find("Player");
            if (playerObj == null)
            {
                playerObj = new GameObject("Player");
            }

            playerObj.transform.position = new Vector3(0, GameConstants.PLAYER_START_Y, 0);
            SpriteRenderer sr = playerObj.GetComponent<SpriteRenderer>();
            if (sr == null) sr = playerObj.AddComponent<SpriteRenderer>();

            // 플레이어 스프라이트 에셋 연결
            string playerSpritePath = "Assets/GameAssets/images/player/player.png";
            Sprite playerSprite = AssetDatabase.LoadAssetAtPath<Sprite>(playerSpritePath);
            if (playerSprite != null)
            {
                sr.sprite = playerSprite;
            }
            else
            {
                Texture2D tex = AssetDatabase.LoadAssetAtPath<Texture2D>(playerSpritePath);
                if (tex != null)
                {
                    TextureImporter importer = AssetImporter.GetAtPath(playerSpritePath) as TextureImporter;
                    if (importer != null && importer.textureType != TextureImporterType.Sprite)
                    {
                        importer.textureType = TextureImporterType.Sprite;
                        importer.SaveAndReimport();
                        sr.sprite = AssetDatabase.LoadAssetAtPath<Sprite>(playerSpritePath);
                    }
                }
            }

            PlayerController controller = playerObj.GetComponent<PlayerController>();
            if (controller == null) controller = playerObj.AddComponent<PlayerController>();

            // 프리팹 연결 (SerializedObject 활용)
            SerializedObject serializedPlayer = new SerializedObject(controller);
            SerializedProperty bulletProp = serializedPlayer.FindProperty("bulletPrefab");
            if (bulletProp != null && bulletPrefabObj != null)
            {
                bulletProp.objectReferenceValue = bulletPrefabObj;
                serializedPlayer.ApplyModifiedProperties();
            }

            Selection.activeGameObject = playerObj;
            EditorUtility.DisplayDialog("Star Invader", "1단계 (카메라, 플레이어, 탄환) 구성이 완료되었습니다!\n\n유니티 상단의 [▶ (Play)] 버튼을 눌러 테스트해 보세요.", "확인");
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

print("Step 1 Unity scripts created successfully!")
