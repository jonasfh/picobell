<?php
declare(strict_types=1);

use Phinx\Migration\AbstractMigration;

final class CreateUserApartmentTable extends AbstractMigration
{
    public function change(): void
    {
        $table = $this->table('user_apartment');
        $table
            ->addColumn('user_id', 'integer', ['signed' => false])
            ->addColumn('apartment_id', 'integer', ['signed' => false])
            ->addColumn('role', 'string', [
                'limit' => 50,
                'default' => 'resident',
            ])
            ->addColumn('created_at', 'timestamp', [
                'default' => 'CURRENT_TIMESTAMP',
            ])
            ->addColumn('modified_at', 'timestamp', [
                'default' => 'CURRENT_TIMESTAMP',
                'update' => 'CURRENT_TIMESTAMP',
            ])
            ->addForeignKey('user_id', 'users', 'id',
                ['delete'=> 'CASCADE', 'update'=> 'NO_ACTION'])
            ->addForeignKey('apartment_id', 'apartments', 'id',
                ['delete'=> 'CASCADE', 'update'=> 'NO_ACTION'])
            ->create();
    }
}
