<?php
declare(strict_types=1);

use Phinx\Seed\AbstractSeed;

final class UsersSeeder extends AbstractSeed
{
    public function run(): void
    {
        $data = [
            [
                'email' => 'testuser@example.com',
                'password_hash' => password_hash('secret123', PASSWORD_DEFAULT),
                'created_at' => date('Y-m-d H:i:s'),
                'modified_at' => date('Y-m-d H:i:s'),
            ],
        ];

        $users = $this->table('users');
        $prefix = $this->getAdapter()->getOption('table_prefix');
        $this->execute("DELETE FROM {$prefix}users WHERE email = 'testuser@example.com'");
        $users->insert($data)->save();
    }

    public function getDependencies(): array
    {
        return [];
    }

}
