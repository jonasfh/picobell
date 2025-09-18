<?php
declare(strict_types=1);

use Phinx\Migration\AbstractMigration;

final class CreateDevicesTable extends AbstractMigration
{
    public function change(): void
    {
        $this->table('devices')
            ->addColumn('user_id', 'integer', ['signed' => false])
            ->addColumn('name', 'string', ['limit' => 255])
            ->addColumn('token', 'string', ['limit' => 512])
            ->addColumn('created_at', 'timestamp', [
                'default' => 'CURRENT_TIMESTAMP',
            ])
            ->addColumn('modified_at', 'timestamp', [
                'default' => 'CURRENT_TIMESTAMP',
                'update'  => 'CURRENT_TIMESTAMP',
            ])
            ->addForeignKey('user_id', 'users', 'id', [
                'delete'=> 'CASCADE',
                'update'=> 'NO_ACTION',
            ])
            ->create();
    }
}
