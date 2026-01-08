<?php
declare(strict_types=1);

use Phinx\Seed\AbstractSeed;

class DeviceSeeder extends AbstractSeed
{
    public function run(): void
    {
        $token = getenv('EMULATOR_DEVICE_TEST_TOKEN');
        if (!$token) {
            echo "⚠️  Missing EMULATOR_DEVICE_TEST_TOKEN in .env\n";
            return;
        }

        $devices = [
            [
                'user_id' => 1, // koblet til første brukeren (Admin)
                'name'    => 'Emulator Device',
                'token'   => $token,
                'created_at' => date('Y-m-d H:i:s'),
                'modified_at' => date('Y-m-d H:i:s'),
            ],
        ];

        $prefix = $this->getAdapter()->getOption('table_prefix');
        $this->execute("DELETE FROM {$prefix}devices WHERE user_id = 1 AND name = 'Emulator Device'");
        $this->table('devices')->insert($devices)->saveData();
    }
    public function getDependencies(): array
    {
        return [
            'UsersSeeder',
        ];
    }

}
